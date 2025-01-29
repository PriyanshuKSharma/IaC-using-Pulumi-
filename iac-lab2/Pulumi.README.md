# **Pulumi Infrastructure Setup - Web Server in AWS**

This README provides an overview of the Pulumi script that sets up a basic web server infrastructure on AWS, including the creation of a Virtual Private Cloud (VPC), subnets, security groups, EC2 instances, a load balancer, and a target group. The script deploys web servers across multiple Availability Zones, attaches them to a load balancer, and exports key information such as IP addresses, hostnames, and the load balancer's DNS name.

---

## **1. Prerequisites**

Before running the script, ensure you have the following:

- **Pulumi** installed on your machine.
- **AWS CLI** configured with appropriate credentials.
- **Python** installed for the Pulumi program.
- **Pulumi AWS SDK** installed via `pip install pulumi_aws`.

---

## **2. Overview of the Infrastructure**

The Pulumi program sets up the following AWS resources:

- **VPC**: A custom Virtual Private Cloud (VPC) with a CIDR block of `10.0.0.0/16`.
- **Internet Gateway (IGW)**: Allows outbound internet access for the resources in the VPC.
- **Route Table**: Routes all outbound traffic (`0.0.0.0/0`) through the Internet Gateway.
- **Security Group**: A security group for the EC2 instances with ingress rules for HTTP (port 80), SSH (port 22), and ICMP (ping), and an egress rule for outbound HTTP traffic.
- **Subnets**: Multiple subnets in different Availability Zones (AZs).
- **Target Group**: An AWS Application Load Balancer (ALB) target group to forward HTTP traffic.
- **Load Balancer**: An Application Load Balancer (ALB) distributing traffic to EC2 instances.
- **EC2 Instances**: A web server instance in each subnet, running a simple HTTP server serving "Hello, World!" from each Availability Zone.
- **Target Group Attachments**: Each EC2 instance is registered as a target in the target group.

---

## **3. Code Explanation**

Here’s a breakdown of each section of the code:

### **3.1 Import Pulumi and AWS Libraries**

```python
import pulumi
import pulumi_aws as aws
```

- We import the `pulumi` library to define the infrastructure as code and `pulumi_aws` to interact with AWS resources.

### **3.2 Get the Latest Amazon Linux 2 AMI**

```python
ami = aws.ec2.get_ami(
    most_recent=True,
    owners=["amazon"],
    filters=[{"name": "name", "values": ["amzn2-ami-hvm-*-x86_64-gp2"]}]
)
```

- This fetches the most recent Amazon Linux 2 AMI for EC2 instances. The filter ensures that only Amazon's official AMIs are selected.

### **3.3 Create a VPC**

```python
vpc = aws.ec2.Vpc("custom-vpc", cidr_block="10.0.0.0/16")
```

- A new VPC is created with a CIDR block of `10.0.0.0/16`.

### **3.4 Create an Internet Gateway (IGW)**

```python
igw = aws.ec2.InternetGateway("custom-igw", vpc_id=vpc.id)
```

- An Internet Gateway is created and attached to the VPC, providing internet access.

### **3.5 Create a Route Table**

```python
route_table = aws.ec2.RouteTable("custom-route-table",
    vpc_id=vpc.id,
    routes=[{
        "cidr_block": "0.0.0.0/0",
        "gateway_id": igw.id
    }]
)
```

- A route table is created with a route that directs all traffic (`0.0.0.0/0`) to the Internet Gateway.

### **3.6 Create a Security Group**

```python
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
```

- A security group is created for the web servers. It allows:
  - Inbound traffic on port 80 (HTTP), port 22 (SSH), and ICMP (ping).
  - Outbound traffic on port 80 to allow HTTP traffic.

### **3.7 Create Subnets in Multiple Availability Zones**

```python
vpc_subnets = []
for idx, az in enumerate(aws.get_availability_zones().names):
    subnet = aws.ec2.Subnet(
        f"custom-subnet-{az}",
        cidr_block=f"10.0.{idx+1}.0/24",
        availability_zone=az,
        map_public_ip_on_launch=True,
        vpc_id=vpc.id
    )
    vpc_subnets.append(subnet)
```

- This loop creates a subnet in each Availability Zone (AZ) in the region and assigns it a unique CIDR block.

### **3.8 Create Target Group**

```python
target_group = aws.lb.TargetGroup(
    "target-group", 
    port=80, 
    protocol="HTTP", 
    target_type="ip", 
    vpc_id=vpc.id
)
```

- A target group is created for the Application Load Balancer (ALB). It listens on port 80 and uses the IP addresses of EC2 instances as targets.

### **3.9 Create Load Balancer (ALB)**

```python
lb = aws.lb.LoadBalancer(
    "loadbalancer",
    internal=False,
    security_groups=[security_group.id],
    subnets=[subnet.id for subnet in vpc_subnets],
    load_balancer_type="application",
)
```

- An Application Load Balancer is created, using the subnets and security group. It is public-facing (`internal=False`).

### **3.10 Create Listener for Load Balancer**

```python
listener = aws.lb.Listener(
    "listener",
    load_balancer_arn=lb.arn,
    port=80,
    default_actions=[{"type": "forward", "target_group_arn": target_group.arn}],
)
```

- A listener is created on port 80 for the ALB, forwarding traffic to the previously defined target group.

### **3.11 Create EC2 Instances in Each Subnet**

```python
for idx, az in enumerate(aws.get_availability_zones().names):
    subnet = vpc_subnets[idx]
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
```

- For each subnet in a different AZ, an EC2 instance is created using the Amazon Linux 2 AMI. A simple Python HTTP server serves the "Hello, World!" message.

### **3.12 Register EC2 Instances with Target Group**

```python
attachment = aws.lb.TargetGroupAttachment(
    f'web-server-{az}',
    target_group_arn=target_group.arn,
    target_id=server.private_ip,
    port=80
)
```

- Each EC2 instance is registered with the target group so that it can receive traffic from the load balancer.

### **3.13 Export Public IPs and Hostnames**

```python
pulumi.export("ips", ips)
pulumi.export("hostnames", hostnames)
pulumi.export("url", lb.dns_name)
```

- The public IPs, hostnames, and the DNS name of the load balancer are exported, which can be used to access the servers and the load balancer.

---

## **4. How to Deploy**

1. **Install Pulumi and AWS CLI**: Ensure that Pulumi is installed and AWS credentials are configured.
2. **Run the Pulumi Program**:
   - In your terminal, navigate to the directory where the script is located.
   - Run `pulumi up` to deploy the infrastructure.
   - Review the changes and confirm the deployment.

3. **Access the Web Servers**:
   - After deployment, Pulumi will output the IP addresses, hostnames, and the load balancer URL. You can access the web servers through the load balancer URL or directly via the public IP addresses.

---

## **5. Cleanup**

To delete the resources created by Pulumi:

```bash
pulumi destroy
```

This will remove all the resources created in the script, such as EC2 instances, load balancer, subnets, and security groups.

---

## **6. Conclusion**

This script demonstrates how to create a basic infrastructure with multiple EC2 instances behind an Application Load Balancer using Pulumi and AWS. It provides a great starting point for more complex infrastructure setups in AWS.

