from aws_cdk import core, aws_dynamodb, aws_lambda, aws_apigateway


class UrlShortenerStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # The code that defines your stack goes here
        table = aws_dynamodb.Table(self, "mapping-table",
            partition_key = aws_dynamodb.Attribute(name="id", type=aws_dynamodb.AttributeType.STRING))
            
        function = aws_lambda.Function(self, "backend",
            runtime=aws_lambda.Runtime.PYTHON_3_7,
            handler='handler.main',
            code=aws_lambda.Code.asset('./lambda'),
            environment={
                'TABLE_NAME': table.table_name
            }
        )
        
        table.grant_read_write_data(function)
        
        api = aws_apigateway.LambdaRestApi(self, "api",handler=function)
        
        
        
