{
  "AWSTemplateFormatVersion" : "2010-09-09",

  "Parameters" : {
    "KeyName": {
      "Description" : "Name of an existing EC2 KeyPair to enable SSH access to the instances",
      "Type": "AWS::EC2::KeyPair::KeyName"
    },
    "LdapServer" : {
      "Type" : "String",
      "Description": "Your LDAP server address"
    },
    "FumApiEndpoint" : {
      "Type" : "String"
    },
    "FumAccessToken" : {
      "Type" : "String",
      "NoEcho" : "True"
    },
    "DBHost" : {
      "Type" : "String"
    },
    "DBName" : {
      "Type" : "String"
    },
    "DBUser" : {
      "Type" : "String"
    },
    "DBPassword" : {
      "Type" : "String",
      "NoEcho" : "True"
    },
    "EmailHost" : {
      "Type" : "String"
    },
    "EmailPort" : {
      "Type" : "String"
    },
    "ProxyUrl" : {
      "Type" : "String",
      "Description" : "Proxy used to access services outside AWS (FUM, smtp, SMS)"
    },
    "SMSGateway" : {
      "Type" : "String"
    },
    "SMSUser" : {
      "Type" : "String"
    },
    "SMSPassword" : {
      "Type" : "String",
      "NoEcho" : "True"
    },
    "Domain" : {
      "Type" : "String"
    },
    "AdminContactEmail" : {
      "Type" : "String"
    },
    "NoticesFromEmail" : {
      "Type" : "String"
    },
    "Subnet" : {
      "Type" : "AWS::EC2::Subnet::Id"
    },
    "Subnet2" : {
      "Type" : "AWS::EC2::Subnet::Id"
    },
    "Vpc" : {
      "Type" : "AWS::EC2::VPC::Id"
    },
    "LoginSecurityGroup" : {
      "Type" : "AWS::EC2::SecurityGroup::Id",
      "Description" : "Security Group that allows database access"
    },
    "SSLCertId" : {
      "Type" : "String"
    }
  },
  "Metadata" : {
    "AWS::CloudFormation::Interface" : {
      "ParameterGroups" : [
        {
          "Label" : { "default" : "Database Configuration" },
          "Parameters" : [ "DBHost", "DBName", "DBUser", "DBPassword"]
        },
        {
          "Label" : {"default" : "FUM connection"},
          "Parameters" : ["FumApiEndpoint", "FumAccessToken"]
        },
        {
          "Label" : {"default" : "Email settings"},
          "Parameters" : ["EmailHost", "EmailPort", "AdminContactEmail"]
        },
        {
          "Label" : {"default" : "SMS settings"},
          "Parameters" : ["SMSGateway", "SMSUser", "SMSPassword"]
        },
        {
          "Label" : {"default" : "Networking"},
          "Parameters" : ["Subnet", "Subnet2", "Vpc", "LoginSecurityGroup", "ProxyUrl"]
        }
      ]
    }
  },

  "Resources" : {
    "LoginGroup": {
      "Type": "AWS::AutoScaling::AutoScalingGroup",
      "Properties": {
        "HealthCheckType" : "ELB",
        "LaunchConfigurationName": { "Ref": "LaunchConfig" },
        "MinSize": "1",
        "MaxSize": "1",
        "DesiredCapacity" : "1",
        "LoadBalancerNames": [ { "Ref": "ElasticLoadBalancer" } ],
        "VPCZoneIdentifier" : [ {"Ref" : "Subnet"}, {"Ref" : "Subnet2"}],
        "HealthCheckGracePeriod" : "300"
      },
      "CreationPolicy": {
        "ResourceSignal": {
          "Count": "1",
          "Timeout": "PT15M"
        }
      }
    },
    "LaunchConfig" : {
      "Type": "AWS::AutoScaling::LaunchConfiguration",
      "Metadata" : {
        "AWS::CloudFormation::Init" : {    
          "config" : {
            "packages" : {
              "yum": {
                "docker" : []
              }
            },
            "services" : {
              "sysvinit" : {
                "docker" : { "enabled" : "true", "ensureRunning" : "true" }
              }
            },
            "files" : {
              "/etc/cron.daily/run-management.sh" : {
                "content" : "docker exec login sso_frontend/manage.py refresh_users\n",
                "mode" : "000755"
              }
            }
          }
        }
      },
      
      "Properties" : {
        "ImageId" : "ami-f9dd458a",
        "UserData" : { "Fn::Base64" : { "Fn::Join" : ["", [
          "#!/bin/bash\n",
          "yum update -y \n",
          "/opt/aws/bin/cfn-init -s ", { "Ref" : "AWS::StackId" }, " -r LaunchConfig ",
          " --region ", { "Ref" : "AWS::Region" }, "\n",
          "docker pull futurice/sso-frontend\n",
          "/opt/aws/bin/cfn-signal -e $? ",
             "         --stack ", { "Ref" : "AWS::StackName" },
             "         --resource LoginGroup ",
             "         --region ", { "Ref" : "AWS::Region" }, "\n",
          "docker run -p 80:8000",
          " --name login",
          " -e FUM_API_ENDPOINT=" , {"Ref" : "FumApiEndpoint"},
          " -e FUM_ACCESS_TOKEN=" , {"Ref" : "FumAccessToken"},
          " -e DB_HOST=" , {"Ref" : "DBHost"},
          " -e DB_NAME=" , {"Ref" : "DBName"},
          " -e DB_USER=" , {"Ref" : "DBUser"},
          " -e DB_PASSWORD=" , {"Ref" : "DBPassword"},
          " -e LDAP_SERVER=" , {"Ref" : "LdapServer"},
          " -e DEBUG=False",
          " -e SCHEME=http",
          " -e SEND_EMAILS=true",
          " -e SECURE_COOKIES=True",
          " -e DOMAIN=" , {"Ref" : "Domain"},
          " -e EMAIL_HOST=" , {"Ref" : "EmailHost"},
          " -e EMAIL_PORT=" , {"Ref" : "EmailPort"},
          " -e ADMIN_CONTACT_EMAIL=" , {"Ref" : "AdminContactEmail"},
          " -e NOTICES_FROM_EMAIL=" , {"Ref" : "NoticesFromEmail"},
          " -e SMS_GATEWAY_URL=" , {"Ref" : "SMSGateway"},
          " -e SMS_USERNAME=" , {"Ref" : "SMSUser"},
          " -e SMS_PASSWORD=" , {"Ref" : "SMSPassword"},
          " -e http_proxy=" , {"Ref" : "ProxyUrl"},
          " -e https_proxy=" , {"Ref" : "ProxyUrl"},
          " -e HTTP_PROXY=" , {"Ref" : "ProxyUrl"},
          " -e HTTPS_PROXY=" , {"Ref" : "ProxyUrl"},
          " -v /home/ec2-user/certs/:/usr/local/share/ca-certificates/",
          " -v /home/ec2-user/saml-certs/:/opt/app/sso_frontend/saml2idp/keys/",
          " futurice/sso-frontend &\n",
          "sleep 20\n",
          "docker exec login ./sso_frontend/manage.py refresh_users\n",
          "\n" ]]
          }
        },
        "KeyName" : { "Ref" : "KeyName" },
        "InstanceType" : "t2.nano",
        "SecurityGroups" : [{ "Fn::GetAtt" : ["LoginEC2SecurityGroup", "GroupId"] }, {"Ref" : "LoginSecurityGroup"}]
      }
    },
    "ElasticLoadBalancer" : {
      "Type" : "AWS::ElasticLoadBalancing::LoadBalancer",
      "Properties" : {
        "Subnets" : [ {"Ref" : "Subnet"}, {"Ref" : "Subnet2"}],
        "Listeners" : [ {
          "LoadBalancerPort" : "443",
          "InstancePort" : "80",
          "InstanceProtocol" : "HTTP",
          "Protocol" : "HTTPS",
          "SSLCertificateId" :   {"Ref" : "SSLCertId" }
        } ],
        "HealthCheck": {
          "Target": "TCP:80",
          "HealthyThreshold": "2",
          "UnhealthyThreshold": "2",
          "Interval": "30",
          "Timeout": "5"
        }, 
        "SecurityGroups" : [{ "Fn::GetAtt" : ["LoginLoadBalancerSecurityGroup", "GroupId"] }]
      }
    },
    "LoginLoadBalancerSecurityGroup" : {
      "Type" : "AWS::EC2::SecurityGroup",
      "Properties" : {
        "GroupDescription" : "Allow HTTPS access to LoadBalancer",
        "SecurityGroupIngress" : {
          "CidrIp" : "0.0.0.0/0",
          "FromPort" : "443",
          "ToPort" : "443",
          "IpProtocol" : "TCP"
        },
        "VpcId" : {"Ref" : "Vpc"}

      }
    },
    "LoginEC2SecurityGroup" : {
      "Type" : "AWS::EC2::SecurityGroup",
      "Properties" : {
        "GroupDescription" : "Allow inbound traffic only from the loadbalancer",
        "SecurityGroupIngress" : {
          "FromPort" : "80",
          "ToPort" : "80",
          "IpProtocol" : "TCP",
          "SourceSecurityGroupId" : {"Fn::GetAtt" : ["LoginLoadBalancerSecurityGroup", "GroupId" ] }
        },
        "VpcId" : {"Ref" : "Vpc"}
      }
    }
  }
}
