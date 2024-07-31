import boto3

ec2 = boto3.client('ec2')

existing_sg_id = 'sg-047f15a9341c57800'  
vpc_id_security_group = 'vpc-0726bbaea85706ec6'  
vpc_id_subnet = 'vpc-08c103a9992de352e'  

while True:
    print("\nSelect an action:")
    print("1. Create security group")
    print("2. Find subnet by CIDR block")
    print("3. Exit")

    choice = input("Enter your choice (1-3): ")

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
                VpcId=vpc_id_security_group,
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
                    {'Name': 'vpc-id', 'Values': [vpc_id_subnet]},
                    {'Name': 'cidr-block', 'Values': cidr_blocks}
                ]
            )
            subnets = response.get('Subnets', [])
            if subnets:
                for subnet in subnets:
                    print(f"Subnet found: {subnet['SubnetId']} ({subnet['CidrBlock']})")
            else:
                print(f"No subnets found with the specified CIDR blocks in VPC '{vpc_id_subnet}'.")
        except Exception as e:
            print(f"Error finding subnet: {e}")

    elif choice == '3':
        print("Exiting...")
        break
    else:
        print("Invalid choice. Please enter a number between 1 and 3.")
