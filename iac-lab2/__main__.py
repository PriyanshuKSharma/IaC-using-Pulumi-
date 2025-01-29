import pulumi
import pulumi_aws as aws
import pulumi
pulumi.export('strVar', 'foo')
pulumi.export('arrVar', ['fizz', 'buzz'])
# open template readme and read contents into stack output
with open('./Pulumi.README.md') as f:
    pulumi.export('readme', f.read())



# Get the latest Amazon Linux 2 AMI
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}]
)

# Create a new VPC
vpc = aws.ec2.Vpc("custom-vpc",
    cidr_block="10.0.0.0/16"
)

# Create an Internet Gateway for internet access
igw = aws.ec2.InternetGateway("custom-igw", vpc_id=vpc.id)

# Create a route table and associate it with the subnet
route_table = aws.ec2.RouteTable("custom-route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id
    }]
)

# Create a security group
security_group = aws.ec2.SecurityGroup(
    "MyWebServer",
    vpc_id=vpc.id,
    ingress=[ 
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "tcp", "from_port": 22, "to_port": 22, "cidr_blocks": ["0.0.0.0/0"]},
        {"protocol": "icmp", "from_port": 8, "to_port": 0, "cidr_blocks": ["0.0.0.0/0"]}
    ],
    egress=[
        {"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]}
    ]
)

# Define subnets in different availability zones
vpc_subnets = []
for idx, az in enumerate(aws.get_availability_zones().names):
    subnet = aws.ec2.Subnet(
        f"custom-subnet-{az}",
        cidr_block=f"10.0.{idx+1}.0/24",  # Correct CIDR block format
        availability_zone=az,
        map_public_ip_on_launch=True,
        vpc_id=vpc.id
    )
    vpc_subnets.append(subnet)

# Create target group first
target_group = aws.lb.TargetGroup(
    "target-group", 
    port=80, 
    protocol="HTTP", 
    target_type="ip", 
    vpc_id=vpc.id
)

# Load Balancer definition
lb = aws.lb.LoadBalancer(
    "loadbalancer",
    internal=False,
    security_groups=[security_group.id],
    subnets=[subnet.id for subnet in vpc_subnets],  # Use the list of subnet IDs here
    load_balancer_type="application",
)

# Create the listener and associate it with the load balancer using the ARN
listener = aws.lb.Listener(
    "listener",
    load_balancer_arn=lb.arn,  # Corrected: using the ARN of the load balancer
    port=80,
    default_actions=[{"type": "forward", "target_group_arn": target_group.arn}],  # Corrected: Use the target group's ARN
)

# Collect public IPs and hostnames
ips = []
hostnames = []

# Loop through each availability zone and create instances
for idx, az in enumerate(aws.get_availability_zones().names):
    subnet = vpc_subnets[idx]  # Use the previously defined subnets

    # Create EC2 instance in each availability zone
    server = aws.ec2.Instance(
        f"web-server-{az}",
        instance_type="t2.micro",
        ami=ami.id,
        subnet_id=subnet.id,
        vpc_security_group_ids=[security_group.id],
        user_data=f"""#!/bin/bash
        echo "Hello, World! from new VPC in {az}" > /var/www/html/index.html
        nohup python3 -m http.server 80 &""",
        tags={"Name": f"web-server-{az}"}
    )

    # Append the instance details
    ips.append(server.public_ip)
    hostnames.append(server.public_dns) 

    attachment = aws.lb.TargetGroupAttachment(
        f'web-server-{az}',
        target_group_arn=target_group.arn,
        target_id=server.private_ip,
        port=80
    )

# Export instance details
pulumi.export("ips", ips)
pulumi.export("hostnames", hostnames)
pulumi.export("url", lb.dns_name)
