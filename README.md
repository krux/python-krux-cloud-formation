# krux-cloud-formation

Krux Python class built on top of `krux-boto` for interacting with [`Troposphere`](https://github.com/cloudtools/troposphere) and `Cloud Formation`.

## Warning

In the current version, `krux_cloud_formation.cloud_formation.CloudFormation` is only compatible with `krux_boto.boto.Boto3` object. Passing other objects, such as `krux_boto.boto.Boto`, will cause an exception.

## Application quick start

The most common use case is to build a CLI script using `krux_s3.cli.Application`.
Here's how to do that:

```python

from krux_s3.cli import Application
from krux_cloud_formation.cloud_formation import CloudFormation

def main():
    # The name must be unique to the organization. The object
    # returned inherits from krux.cli.Application, so it provides
    # all that functionality as well.
    app = Application(name='krux-my-boto-script')

    cloud_formation = CloudFormation(boto=app.boto3, s3=app.s3)

    # Do magic with cloud_formation.template

    cloud_formation.save()

### Run the application stand alone
if __name__ == '__main__':
    main()

```

As long as you get an instance of `krux_boto.boto.Boto3`, the rest are the same. Refer to `krux_boto` module's [README](https://github.com/krux/python-krux-boto/blob/master/README.md) on various ways to instanciate the class.
