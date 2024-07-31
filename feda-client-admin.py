import boto3

ec2 = boto3.client('ec2')
s3 = boto3.client('s3')

existing_sg_id = 'sg-047f15a9341c57800'  # Replace with your actual existing security group ID
security_group_vpc_id = 'vpc-0726bbaea85706ec6'
subnet_vpc_id = 'vpc-08c103a9992de352e'

while True:
    print("\nSelect an action:")
    print("1. Create security group")
    print("2. Find subnet by CIDR block")
    print("3. Get S3 bucket ARN")
    print("4. Exit")

    choice = input("Enter your choice (1-4): ")

    if choice == '1':
        # 1. Create Security Group
        new_sg_name = input("Enter the desired name for the new security group: ")
        description = input("Enter the desired description for the new security group: ")
        tag_key = "Name"
        tag_value = input(f"Enter the value for the '{tag_key}' tag: ")

        try:
            response = ec2.create_security_group(
                GroupName=new_sg_name,
                Description=description,
                VpcId=security_group_vpc_id,
                TagSpecifications=[
                    {
                        'ResourceType': 'security-group',
                        'Tags': [{'Key': tag_key, 'Value': tag_value}]
                    }
                ]
            )
            new_sg_id = response['GroupId']
            print(f"New security group '{new_sg_name}' created with ID: {new_sg_id}")

            copy_rules = input("Do you want to copy rules from the existing security group? (yes/no): ")
            if copy_rules.lower() == 'yes':
                response = ec2.describe_security_groups(GroupIds=[existing_sg_id])
                for rule in response['SecurityGroups'][0]['IpPermissions']:
                    ec2.authorize_security_group_ingress(GroupId=new_sg_id, IpPermissions=[rule])
                print("Rules copied successfully.")

        except Exception as e:
            print(f"Error creating security group: {e}")

    elif choice == '2':  
        # 2. Find Subnet by CIDR Block
        cidr_blocks = []
        while True:
            cidr_block = input("Enter a CIDR block to search for (or type 'done' to finish): ")
            if cidr_block.lower() == 'done':
                break
            cidr_blocks.append(cidr_block)

        try:
            response = ec2.describe_subnets(
                Filters=[
                    {'Name': 'vpc-id', 'Values': [subnet_vpc_id]},
                    {'Name': 'cidr-block', 'Values': cidr_blocks}
                ]
            )
            subnets = response.get('Subnets', [])
            if subnets:
                for subnet in subnets:
                    print(f"Subnet found: {subnet['SubnetId']} ({subnet['CidrBlock']})")
            else:
                print(f"No subnets found with the specified CIDR blocks in VPC '{subnet_vpc_id}'.")
        except Exception as e:
            print(f"Error finding subnet: {e}")

    elif choice == '3':
        # 3. Get S3 Bucket ARN
        bucket_name = input("Enter the S3 bucket name: ")
        try:
            response = s3.get_bucket_location(Bucket=bucket_name)
            location = response['LocationConstraint']
            arn = f"arn:aws:s3:::{bucket_name}"
            if location:
                arn += f" ({location})"
            print(f"S3 bucket ARN: {arn}")
        except Exception as e:
            print(f"Error getting S3 bucket ARN: {e}")

    elif choice == '4':  
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 4.")
