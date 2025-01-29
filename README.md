# Pulumi Infrastructure-as-Code (IaC) Implementation

This repository contains the infrastructure code for deploying cloud resources using Pulumi. It demonstrates the implementation of various AWS services, including EC2 instances, load balancers, subnets, security groups, and more, using Pulumi's Python SDK.

---

## **Overview**

This project leverages **Pulumi** to define and provision cloud infrastructure in an easy-to-use and consistent manner. Pulumi allows you to manage your cloud resources using general-purpose programming languages such as Python, TypeScript, and Go, while providing strong integrations with major cloud providers like AWS, Azure, and GCP.

The resources deployed by this project include:

- **VPC**: Virtual Private Cloud
- **Subnets**: Public and private subnets across different Availability Zones (AZs)
- **Security Groups**: Configurations for controlling inbound and outbound traffic
- **EC2 Instances**: Virtual machines with basic user data to serve web content
- **Application Load Balancer (ALB)**: Used to distribute incoming web traffic
- **Target Group**: Manages the EC2 instances behind the ALB
- **IAM Policies**: For managing the necessary permissions for resources

---

## **Prerequisites**

Before you can use this Pulumi project, you need the following:

- **Pulumi**: Install Pulumi on your machine. You can follow the [official Pulumi installation guide](https://www.pulumi.com/docs/get-started/install/).
- **AWS CLI**: Ensure that the AWS CLI is installed and configured. If not, follow [this guide](https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-quickstart.html).
- **Python 3.6+**: Ensure Python 3.6 or later is installed on your system.
- **AWS Account**: You must have an active AWS account and sufficient permissions to create resources such as VPCs, EC2 instances, and load balancers.

---

## **Setting Up the Project**

### 1. **Clone the Repository**

Clone this repository to your local machine:

```bash
git clone https://github.com/PriyanshuKSharma/IaC-using-Pulumi-.git
cd IaC-using-Pulumi-
```

### 2. **Install Dependencies**

Ensure that you have the required Python dependencies installed. You can install them using `pip`:

```bash
pip install -r requirements.txt
```

### 3. **Configure AWS Credentials**

Pulumi uses the AWS SDK to create resources, so you need to set up your AWS credentials. You can configure the AWS CLI with the following command:

```bash
aws configure
```

Alternatively, you can set the credentials using environment variables:

```bash
export AWS_ACCESS_KEY_ID=<your-access-key-id>
export AWS_SECRET_ACCESS_KEY=<your-secret-access-key>
export AWS_DEFAULT_REGION=us-east-1
```

### 4. **Login to Pulumi**

Login to Pulumi using your Pulumi account:

```bash
pulumi login
```

If this is your first time using Pulumi, you'll be prompted to sign up or log in to your Pulumi account.

---

## **Deploying the Infrastructure**

To deploy the infrastructure defined in this project, run the following Pulumi commands:

1. **Preview the changes**: This will show what resources Pulumi plans to create, update, or delete.

    ```bash
    pulumi preview
    ```

2. **Deploy the infrastructure**: This command will actually create the resources defined in your Pulumi code.

    ```bash
    pulumi up
    ```

    During the `pulumi up` process, Pulumi will prompt you to confirm the changes before proceeding.

3. **Check the output**: After the deployment, Pulumi will display the output of the resources (such as the URL of the load balancer).

    ```bash
    pulumi stack output
    ```

---

## **Managing the Infrastructure**

### 1. **View the Stack's Status**

To view the status of your resources, run:

```bash
pulumi stack
```

### 2. **Update the Stack**

If you make changes to the infrastructure code, you can apply those changes by running:

```bash
pulumi up
```

### 3. **Destroy the Stack**

To delete all resources managed by Pulumi, run:

```bash
pulumi destroy
```

This will prompt you for confirmation before deleting the resources.

---

## **Code Overview**

Here is a summary of the main code and resources defined in this project:

### **VPC Creation**

Creates a Virtual Private Cloud (VPC) with a specified CIDR block.

```python
vpc = aws.ec2.Vpc("custom-vpc", cidr_block="10.0.0.0/16")
```

### **Subnet Creation**

Creates subnets in different availability zones (AZs) within the VPC.

```python
vpc_subnets = []
for idx, az in enumerate(aws.get_availability_zones().names):
    subnet = aws.ec2.Subnet(f"custom-subnet-{az}", cidr_block=f"10.0.{idx+1}.0/24", availability_zone=az, map_public_ip_on_launch=True, vpc_id=vpc.id)
    vpc_subnets.append(subnet)
```

### **Security Group**

Creates a security group to control inbound and outbound traffic for EC2 instances.

```python
security_group = aws.ec2.SecurityGroup("MyWebServer", vpc_id=vpc.id, ingress=[{"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]}], egress=[{"protocol": "tcp", "from_port": 80, "to_port": 80, "cidr_blocks": ["0.0.0.0/0"]}])
```

### **Load Balancer**

Creates an Application Load Balancer (ALB) to distribute traffic to backend EC2 instances.

```python
lb = aws.lb.LoadBalancer("loadbalancer", internal=False, security_groups=[security_group.id], subnets=[subnet.id for subnet in vpc_subnets])
```

### **Target Group**

Creates a target group for the ALB to route traffic to the EC2 instances.

```python
target_group = aws.lb.TargetGroup("target-group", port=80, protocol="HTTP", target_type="ip", vpc_id=vpc.id)
```

### **EC2 Instances**

Creates EC2 instances with a basic HTTP server.

```python
server = aws.ec2.Instance(f"web-server-{az}", instance_type="t2.micro", ami=ami.id, subnet_id=subnet.id, vpc_security_group_ids=[security_group.id], user_data=f"""#!/bin/bash echo "Hello, World!" > /var/www/html/index.html nohup python3 -m http.server 80 &""")
```

---

## **Troubleshooting and Known Issues**

- **Missing Permissions**: Ensure that your AWS user has the necessary permissions to create resources such as EC2 instances, VPCs, subnets, and load balancers.
- **IAM Policy Errors**: If encountering permission issues, update your IAM policy to allow actions related to Elastic Load Balancing, EC2, and VPC management.

Refer to the detailed documentation in the repository for additional error troubleshooting and mitigation.

---

## **Contributing**

If you'd like to contribute to this project, feel free to fork the repository, make your changes, and submit a pull request. Contributions, improvements, and bug fixes are always welcome!

---

## **License**

This project is not licensed.


--- 

By following the instructions in this README, you'll be able to deploy and manage cloud infrastructure using Pulumi effectively.

