# Snowplow pipeline support

The Objectiv collector supports using the Snowplow pipeline as a sink for Objectiv events. Currently, there is support 
for Google PubSub and AWS SQS/Kinesis, using Thrift messages. This means we by-pass the Snowplow collector, but hook 
directly into Snowplows enrichment step.

Please see https://objectiv.io/docs/tracking/collector/snowplow-pipeline for more information.

# Maintenance

## Thrift schema
Compiling the Thrift schema into Python (should normally not be needed). The schema looks like this:
```java
namespace java com.snowplowanalytics.snowplow.CollectorPayload.thrift.model1

struct CollectorPayload {
  31337: string schema

  // Required fields which are intrinsic properties of HTTP
  100: string ipAddress

  // Required fields which are Snowplow-specific
  200: i64 timestamp
  210: string encoding
  220: string collector

  // Optional fields which are intrinsic properties of HTTP
  300: optional string userAgent
  310: optional string refererUri
  320: optional string path
  330: optional string querystring
  340: optional string body
  350: optional list<string> headers
  360: optional string contentType

  // Optional fields which are Snowplow-specific
  400: optional string hostname
  410: optional string networkUserId
}
```
source: https://github.com/snowplow/snowplow/blob/master/2-collectors/thrift-schemas/collector-payload-1/src/main/thrift/collector-payload.thrift

The Python code can then be generated using:
```shell
  curl https://raw.githubusercontent.com/snowplow/snowplow/master/2-collectors/thrift-schemas/collector-payload-1/src/main/thrift/collector-payload.thrift
  thrift --gen py  collector-payload.thrift
```
This will create a dir `gen-py/schema/`, containing `constants.py` and `ttypes.py`. These need to be copied into 
`backend/objeciv_bach/snowplow/schema`.
