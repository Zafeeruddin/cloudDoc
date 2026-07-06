# Lambda Authorizer Placeholder

This authorizer is intentionally simple. It validates a mocked bearer token with the format:

`Bearer docops:<user_id>:<email>:<display_name>`

It returns an HTTP API simple response (`isAuthorized`) plus context fields. In a production build you would replace this with real JWT validation against your IdP and use API Gateway parameter mapping to inject trusted identity headers to the backend.

## Packaging

```bash
cd infra/lambda-authorizer
zip -r authorizer.zip handler.py
```

Use the resulting `authorizer.zip` with the Terraform variable `lambda_authorizer_package_path`.
