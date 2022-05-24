from aws_assume_role.exceptions import AwsAssumeBaseException


class CmdBaseException(AwsAssumeBaseException):
    pass


class InvalidArgumentsException(AwsAssumeBaseException):
    pass


class InvalidKeyException(AwsAssumeBaseException):
    pass
