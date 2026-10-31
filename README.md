# Client Brief Extractor API

## Extract a brief

Send a JSON object to `POST /briefs/extract`. The request accepts either
`message` or `prompt` as the key containing the client brief:

```json
{
  "message": "I own a furniture business and need an ecommerce website. My budget is PHP 120,000."
}
```

The value must contain 10-10,000 non-whitespace characters. Request validation
errors return `422`; extraction-provider failures return `502`. A `422` means
the request body is missing the brief, uses an unsupported field name, or has
an invalid value; it does not mean the brief's content was rejected.

Extraction rules are sent to the model as system instructions, separately from
the client message, so text inside the brief is treated as untrusted data.
