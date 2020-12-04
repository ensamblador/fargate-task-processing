from aws_cdk import (
    aws_ec2,
    aws_ecs,
    aws_ecr,
    aws_ecs_patterns,
    aws_servicediscovery,
    aws_iam,
    core,
)

from os import getenv


# Creating a construct that will populate the required objects created in the platform repo such as vpc, ecs cluster, and service discovery namespace
class BasePlatform(core.Construct):
    
    def __init__(self, scope: core.Construct, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)
        self.environment_name = 'base-infra-ecs'

        # The base platform stack is where the VPC was created, so all we need is the name to do a lookup and import it into this stack for use
        self.vpc = aws_ec2.Vpc.from_lookup(
            self, "VPC",
            vpc_name='{}/BaseVPC'.format(self.environment_name)
        )
        
        self.sd_namespace = aws_servicediscovery.PrivateDnsNamespace.from_private_dns_namespace_attributes(
            self, "SDNamespace",
            namespace_name=core.Fn.import_value('NSNAME'),
            namespace_arn=core.Fn.import_value('NSARN'),
            namespace_id=core.Fn.import_value('NSID')
        )
        
        self.ecs_cluster = aws_ecs.Cluster.from_cluster_attributes(
            self, "ECSCluster",
            cluster_name=core.Fn.import_value('ECSClusterName'),
            security_groups=[],
            vpc=self.vpc,
            default_cloud_map_namespace=self.sd_namespace
        )
        
        self.services_sec_grp = aws_ec2.SecurityGroup.from_security_group_id(
            self, "ServicesSecGrp",
            security_group_id=core.Fn.import_value('ServicesSecGrp')
        )


class QueueProcessingService(core.Stack):
    
    def __init__(self, scope: core.Stack, id: str, **kwargs):
        super().__init__(scope, id, **kwargs)

        self.base_platform = BasePlatform(self, self.stack_name)


        self.fargate_queue_processing_service = aws_ecs_patterns.QueueProcessingFargateService (
            self, "QueueProcessingService",
            service_name='queue-processing',
            cluster=self.base_platform.ecs_cluster,
            cpu=256,
            desired_task_count=0,
            max_scaling_capacity=10,
            memory_limit_mib=512,
            #image=aws_ecs.ContainerImage.from_registry("625806755153.dkr.ecr.us-east-1.amazonaws.com/python-workers:latest"), 
            image=aws_ecs.ContainerImage.from_ecr_repository(
                aws_ecr.Repository.from_repository_name(self, 
                "mi_repositorio", 
                "python-workers")),
            environment={"REGION": getenv('AWS_DEFAULT_REGION'), "AWS_ACCOUNT_ID": getenv('AWS_ACCOUNT_ID'),},


        )

        
        self.fargate_queue_processing_service.task_definition.add_to_task_role_policy(
            aws_iam.PolicyStatement(
                actions=['ec2:DescribeSubnets'],
                resources=['*']
            )
        )
        
        #self.fargate_queue_processing_service.service.connections.allow_to(
        #    self.base_platform.services_sec_grp,
        #    port_range=aws_ec2.Port(protocol=aws_ec2.Protocol.TCP, string_representation="frontendtobackend", from_port=3000, to_port=3000)
        #)
        


_env = core.Environment(account=getenv('AWS_ACCOUNT_ID'), region=getenv('AWS_DEFAULT_REGION'))
environment = "python-queue-tasks"
stack_name = "{}".format(environment)
app = core.App()
QueueProcessingService(app, stack_name, env=_env)
app.synth()
