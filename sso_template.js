{
  "AWSTemplateFormatVersion" : "2010-09-09",

  "Parameters" : {
    "KeyName": {
      "Description" : "Name of an existing EC2 KeyPair to enable SSH access to the instances",
      "Type": "String",
      "MinLength": "1",
      "MaxLength": "255",
      "AllowedPattern" : "[\\x20-\\x7E]*",
      "ConstraintDescription" : "can contain only ASCII characters."
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
    "SecurityGroup1" : {
      "Type" : "AWS::EC2::SecurityGroup::Id"
    },
    "SecurityGroup2" : {
      "Type" : "AWS::EC2::SecurityGroup::Id"
    },
    "Subnet" : {
      "Type" : "AWS::EC2::Subnet::Id"
    }
  },
  "Metadata" : {
    "AWS::CloudFormation::Interface" : {
      "ParameterGroups" : [
        {
          "Label" : { "default" : "Database Configuration" },
          "Parameters" : [ "DBHost", "DBName", "DBUser", "DBPassword"]
        }
      ]
    }
  },

  "Resources" : {
  	"Login" : {
  		"Type": "AWS::EC2::Instance",
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
            }
          }
  			}
      },
  		
      "Properties" : {
        "ImageId" : "ami-4cdd453f",
        "UserData" : { "Fn::Base64" : { "Fn::Join" : ["", [
          "#!/bin/bash\n",
          "yum update -y \n",
          "/opt/aws/bin/cfn-init -s ", { "Ref" : "AWS::StackId" }, " -r Login ",
          " --region ", { "Ref" : "AWS::Region" }, "\n",
          "docker pull futurice/sso-frontend\n",
          "docker run -p 80:8000",
          " -e FUM_API_ENDPOINT=" , {"Ref" : "FumApiEndpoint"},
          " -e FUM_ACCESS_TOKEN=" , {"Ref" : "FumAccessToken"},
          " -e DB_HOST=" , {"Ref" : "DBHost"},
          " -e DB_NAME=" , {"Ref" : "DBName"},
          " -e DB_USER=" , {"Ref" : "DBUser"},
          " -e DB_PASSWORD=" , {"Ref" : "DBPassword"},
          " -e LDAP_SERVER=" , {"Ref" : "LdapServer"},
          " futurice/sso-frontend",
          "\n" ]]
          }
        },
        "KeyName" : { "Ref" : "KeyName" },
        "SecurityGroupIds" : [{"Ref" : "SecurityGroup1"}, {"Ref" : "SecurityGroup2"}],
        "SubnetId" :  {"Ref" : "Subnet"}
      }
    }
  },

  "Outputs" : {
    "WebsiteURL" : {
      "Value" : { "Fn::Join" : ["", ["http://", { "Fn::GetAtt" : [ "Login", "PublicDnsName" ]}]] }
    }
  }
}
