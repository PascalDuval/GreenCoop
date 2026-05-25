Procedure Option 2 (Replica Set) - Build, Push, Deploy, Test

Legend:
- LOCAL = on your PC (not in SSH)
- SSH = inside the EC2 SSH session
- ONE-TIME = run once unless the instance is rebuilt
- REPEAT = run each time you redeploy/tests

SECTION A - Build and push image (LOCAL, REPEAT)
1) Build image
   cd C:\Users\karap\OpenClassRooms\projet8-docker
   docker build --no-cache -t projet8-docker-data-migration .

2) Tag + push to ECR
   (If not logged in to ECR)
   aws ecr get-login-password --region eu-north-1 | docker login --username AWS --password-stdin 443134358700.dkr.ecr.eu-north-1.amazonaws.com
   docker tag projet8-docker-data-migration:latest 443134358700.dkr.ecr.eu-north-1.amazonaws.com/projet8-docker-data-migration:latest
   docker push 443134358700.dkr.ecr.eu-north-1.amazonaws.com/projet8-docker-data-migration:latest

SECTION B - EC2 preparation (LOCAL then SSH, ONE-TIME)
3) Copy files to EC2 (LOCAL, ONE-TIME)
   scp -i "C:\Users\karap\OpenClassRooms\projet8-docker\data\dataprojet8-key.pem" "C:\Users\karap\OpenClassRooms\projet8-docker\docker-compose-minimal.yml" ec2-user@51.20.1.167:~/
   scp -i "C:\Users\karap\OpenClassRooms\projet8-docker\data\dataprojet8-key.pem" -r "C:\Users\karap\OpenClassRooms\projet8-docker\scripts-replica" ec2-user@51.20.1.167:~/

4) Connect to EC2 (LOCAL -> SSH)
   ssh -i "C:\Users\karap\OpenClassRooms\projet8-docker\data\dataprojet8-key.pem" ec2-user@51.20.1.167

5) Verify files on EC2 (SSH)
   ls -la ~/docker-compose-minimal.yml
   ls -la ~/scripts-replica

6) Install Docker Compose (SSH, ONE-TIME)
   If docker compose is missing:
   - Plugin install (recommended):
     sudo mkdir -p /usr/local/lib/docker/cli-plugins
     sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64" -o /usr/local/lib/docker/cli-plugins/docker-compose
     sudo chmod +x /usr/local/lib/docker/cli-plugins/docker-compose
     docker compose version

   - Or docker-compose v1 (pip):
     sudo yum install -y python3-pip
     pip3 install --user docker-compose
     docker-compose -f docker-compose-minimal.yml up -d

SECTION C - Start replica set (SSH, ONE-TIME per instance)
7) Start replica set
   docker compose -f docker-compose-minimal.yml up -d
   docker ps
   Note: Docker Compose prefixes the network name.
   Check the real network name:
   docker network ls | grep mongo-cluster

SECTION D - Test migration image (SSH, REPEAT)
8) Pull image
   docker pull 443134358700.dkr.ecr.eu-north-1.amazonaws.com/projet8-docker-data-migration:latest

9) Run tests (replica set enabled)
   IMPORTANT: run the container on the same Docker network so it can resolve mongo1/mongo2/mongo3.
   Use the network name shown by:
   docker network ls | grep mongo-cluster
   Example (if network is "ec2-user_mongo-cluster"):
   docker run --rm --name data-migration --network ec2-user_mongo-cluster \

   If the name "data-migration" already exists:
   docker rm -f data-migration

   docker run --rm --name data-migration --network <NETWORK_NAME_FROM_DOCKER_NETWORK_LS> \
     -e ENABLE_REPLICA_TESTS=true \
     -e MONGO_URI="mongodb://mongo1:27017" \
     -e MONGO_PRIMARY_URI="mongodb://mongo1:27017/?replicaSet=rsGreenCoop" \
     -e MONGO_PRIMARY_ADMIN_URI="mongodb://admin:admin123@mongo1:27017/admin?replicaSet=rsGreenCoop" \
     -e MONGO_REPLICA_URI="mongodb://analyste:readonly123@mongo1:27017,mongo2:27017,mongo3:27017/GreenCoop?replicaSet=rsGreenCoop" \
     -e MONGO_CLONE_SECONDARY_URI="mongodb://analyste:readonly123@mongo3:27017/GreenCoop?directConnection=true" \
     443134358700.dkr.ecr.eu-north-1.amazonaws.com/projet8-docker-data-migration:latest

SECTION E - Cleanup (SSH, OPTIONAL)
10) Stop replica set
    docker compose -f docker-compose-minimal.yml down -v

SECTION F - CloudWatch monitoring + logs (SSH, ONE-TIME)
11) Attach IAM role (AWS Console, ONE-TIME)
    Role must include policy: CloudWatchAgentServerPolicy

12) Enable detailed monitoring (AWS Console, ONE-TIME)
    EC2 -> Instance -> Actions -> Monitor and troubleshoot -> Manage detailed monitoring -> Enable

13) Install CloudWatch Agent (SSH, ONE-TIME)
    Amazon Linux 2/2023:
      sudo yum install -y amazon-cloudwatch-agent
    Ubuntu:
      sudo apt-get update
      sudo apt-get install -y amazon-cloudwatch-agent

14) Create agent config (SSH, ONE-TIME)
    sudo mkdir -p /opt/aws/amazon-cloudwatch-agent/etc
    sudo tee /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json > /dev/null <<'JSON'
    {
      "agent": {
        "metrics_collection_interval": 60,
        "region": "eu-north-1"
      },
      "metrics": {
        "namespace": "EC2/Custom",
        "append_dimensions": {
          "InstanceId": "${aws:InstanceId}"
        },
        "metrics_collected": {
          "cpu": {
            "measurement": ["cpu_usage_idle","cpu_usage_iowait","cpu_usage_user","cpu_usage_system"],
            "metrics_collection_interval": 60
          },
          "disk": {
            "measurement": ["used_percent"],
            "resources": ["*"],
            "metrics_collection_interval": 60
          },
          "mem": {
            "measurement": ["mem_used_percent"],
            "metrics_collection_interval": 60
          },
          "netstat": {
            "measurement": ["tcp_established","tcp_time_wait"]
          }
        }
      },
      "logs": {
        "logs_collected": {
          "files": {
            "collect_list": [
              {
                "file_path": "/var/log/messages",
                "log_group_name": "/ec2/system/messages",
                "log_stream_name": "{instance_id}"
              },
              {
                "file_path": "/var/log/cloud-init.log",
                "log_group_name": "/ec2/system/cloud-init",
                "log_stream_name": "{instance_id}"
              },
              {
                "file_path": "/var/lib/docker/containers/*/*.log",
                "log_group_name": "/ec2/docker/containers",
                "log_stream_name": "{instance_id}"
              }
            ]
          }
        }
      }
    }
    JSON

    Ubuntu only:
      sudo sed -i 's|/var/log/messages|/var/log/syslog|g' /opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json

15) Start agent (SSH, ONE-TIME)
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl \
      -a fetch-config -m ec2 \
      -c file:/opt/aws/amazon-cloudwatch-agent/etc/amazon-cloudwatch-agent.json -s

16) Check agent status (SSH)
    sudo /opt/aws/amazon-cloudwatch-agent/bin/amazon-cloudwatch-agent-ctl -m ec2 -a status

17) View logs in CloudWatch (AWS Console)
    CloudWatch -> Logs -> Log groups:
      /ec2/system/messages (or /ec2/system/syslog on Ubuntu)
      /ec2/system/cloud-init
      /ec2/docker/containers

18) (Optional) Interact to generate logs and watch them evolve (SSH)
    - Docker live logs:
      docker logs -f mongo1
    - Generate a Mongo log entry:
      docker exec -it mongo1 mongosh --eval "db.getSiblingDB('admin').runCommand({ping:1})"
    - Tail the Docker JSON log directly (replace <id>):
      docker ps --no-trunc | grep mongo1
      sudo tail -f /var/lib/docker/containers/<id>/<id>-json.log

SECTION G - Monitoring guide (EC2 + CloudWatch, EASY)
19) Quick EC2 checks (SSH)
    - Confirm containers:
      docker ps
    - Live container logs:
      docker logs -f mongo1
    - System resources (host):
      top
      df -h
      free -m
    - Container resources:
      docker stats

20) Confirm CloudWatch logs are flowing (AWS Console)
    CloudWatch -> Logs -> Log groups:
      /ec2/system/messages (or /ec2/system/syslog on Ubuntu)
      /ec2/system/cloud-init
      /ec2/docker/containers
    Open a log stream and verify new lines appear after running:
      docker exec -it mongo1 mongosh --eval "db.getSiblingDB('admin').runCommand({ping:1})"

21) Create a simple CloudWatch dashboard (AWS Console)
    - CloudWatch -> Dashboards -> Create dashboard
    - Add widget -> Line
      Namespace: EC2/Custom
      Metrics:
        - mem_used_percent
        - disk_used_percent (resource: /)
        - cpu_usage_user or cpu_usage_system
    - Add widget -> Line
      Namespace: AWS/EC2
      Metric: CPUUtilization
    - Save dashboard

22) Optional alarms (AWS Console)
    - CPUUtilization > 80% for 5 minutes
    - mem_used_percent > 80% for 5 minutes
    - disk_used_percent > 80% for 5 minutes

SECTION H - Mongo queries from EC2 (SSH)
23) Quick shell
    docker exec -it mongo1 mongosh

24) Useful one-liners
    docker exec -it mongo1 mongosh --eval "show dbs"
    docker exec -it mongo1 mongosh --eval "db.getSiblingDB('GreenCoop').getCollectionNames()"
    docker exec -it mongo1 mongosh --eval "db.getSiblingDB('GreenCoop').orders.findOne()"

25) Example: temperature evolution in Lille (adapt to your schema)
    Assumptions:
      - database: GreenCoop
      - collection: meteo
      - fields: city (string), date (ISODate), temperature (number)

    Aggregate by day (average temperature):
      docker exec -it mongo1 mongosh --eval "db.getSiblingDB('GreenCoop').meteo.aggregate([ \
        { $match: { city: 'Lille', date: { $gte: ISODate('2024-01-01'), $lt: ISODate('2024-02-01') } } }, \
        { $group: { _id: { $dateToString: { format: '%Y-%m-%d', date: '$date' } }, avgTemp: { $avg: '$temperature' } } }, \
        { $sort: { _id: 1 } } \
      ])"

    If your field names differ, replace city/date/temperature/collection.

26) Graph options
    - Quick export to CSV for graphing:
      docker exec -it mongo1 mongosh --quiet --eval "db.getSiblingDB('GreenCoop').meteo.aggregate([ \
        { $match: { city: 'Lille' } }, \
        { $group: { _id: { $dateToString: { format: '%Y-%m-%d', date: '$date' } }, avgTemp: { $avg: '$temperature' } } }, \
        { $sort: { _id: 1 } } \
      ]).forEach(d => print(d._id + ',' + d.avgTemp))" > lille_temp.csv
    - Open lille_temp.csv locally and plot in Excel/Sheets.
