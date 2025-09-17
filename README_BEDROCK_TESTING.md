# AWS Bedrock Testing Results

## Summary

We successfully tested AWS Bedrock with various Claude models and created comprehensive examples for invoking Bedrock prompts using the boto3 library.

## ✅ Working Models

The following models are confirmed working with on-demand throughput:

1. **Claude 3 Haiku** (`anthropic.claude-3-haiku-20240307-v1:0`)
   - Fast and cost-effective
   - Great for quick responses and simple tasks
   - ✅ **RECOMMENDED for most use cases**

2. **Claude 3 Sonnet** (`anthropic.claude-3-sonnet-20240229-v1:0`)
   - More capable than Haiku
   - Good balance of performance and cost
   - ✅ **RECOMMENDED for complex tasks**

3. **Amazon Titan Text** (`amazon.titan-text-express-v1`)
   - AWS's own model
   - Good for general text generation
   - ✅ **RECOMMENDED for AWS-native applications**

## ❌ Models Requiring Inference Profiles

The following newer models require inference profiles and cannot be used with on-demand throughput:

- Claude 4 Sonnet (`anthropic.claude-sonnet-4-20250514-v1:0`)
- Claude 3.5 Sonnet (`anthropic.claude-3-5-sonnet-20241022-v2:0`)
- Claude 3.7 Sonnet (`anthropic.claude-3-7-sonnet-20250219-v1:0`)
- Claude 3.5 Haiku (`anthropic.claude-3-5-haiku-20241022-v1:0`)

## 📁 Files Created

### Core Files
1. **`bedrock_boto3_demo.py`** - Comprehensive demo with multiple models
2. **`bedrock_simple_example.py`** - Simple, focused examples
3. **`bedrock_config.py`** - Configuration and setup utilities
4. **`bedrock_prompt_management.py`** - Bedrock Prompt Management examples
5. **`bedrock_invoke_prompt.py`** - Simple prompt invocation
6. **`bedrock_prompt_utils.py`** - Utility functions for prompt management

### Test Files
1. **`test_claude4_sonnet.py`** - Initial test for Claude 4 (failed due to inference profile requirement)
2. **`simple_claude4_test.py`** - Basic model testing
3. **`test_working_claude.py`** - Test of newer models (failed due to inference profile requirement)
4. **`test_final_working.py`** - ✅ **FINAL SUCCESSFUL TEST**

## 🚀 Quick Start

### Basic Usage
```python
import boto3
import json

# Initialize client
bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')

# Claude 3 Haiku (recommended)
model_id = "anthropic.claude-3-haiku-20240307-v1:0"

# Prepare request
body = {
    "anthropic_version": "bedrock-2023-05-31",
    "max_tokens": 1000,
    "messages": [
        {
            "role": "user",
            "content": "Your prompt here"
        }
    ]
}

# Invoke model
response = bedrock_client.invoke_model(
    modelId=model_id,
    body=json.dumps(body),
    contentType="application/json"
)

# Parse response
response_body = json.loads(response['body'].read())
for content_block in response_body['content']:
    if content_block['type'] == 'text':
        print(content_block['text'])
```

### Prompt Template Concept
```python
# Template with variables
template = "You are an expert {role}. Help with {topic}."

# Substitute variables
variables = {"role": "AI researcher", "topic": "machine learning"}
final_prompt = template
for key, value in variables.items():
    final_prompt = final_prompt.replace(f"{{{key}}}", value)

# Use with any working model
```

## 🔧 Setup Requirements

1. **AWS Credentials**: Configure with `aws configure`
2. **Dependencies**: Install with `pip install -r requirements.txt`
3. **Model Access**: Request access in AWS Bedrock console
4. **IAM Permissions**: 
   - `bedrock:InvokeModel`
   - `bedrock:InvokeModelWithResponseStream`
   - `bedrock:GetFoundationModel`
   - `bedrock:ListFoundationModels`

## 🧪 Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run the successful test
python test_final_working.py

# Run individual examples
python bedrock_simple_example.py
python bedrock_boto3_demo.py
```

## 📊 Test Results

| Model | Status | Notes |
|-------|--------|-------|
| Claude 3 Haiku | ✅ Working | Fast, cost-effective |
| Claude 3 Sonnet | ✅ Working | More capable |
| Amazon Titan Text | ✅ Working | AWS native |
| Claude 4 Sonnet | ❌ Requires inference profile | Not available with on-demand |
| Claude 3.5 Sonnet | ❌ Requires inference profile | Not available with on-demand |
| Claude 3.7 Sonnet | ❌ Requires inference profile | Not available with on-demand |

## 🎯 Recommendations

1. **Start with Claude 3 Haiku** for most applications
2. **Use Claude 3 Sonnet** for more complex tasks
3. **Implement prompt templates** with variable substitution
4. **Consider inference profiles** for newer models when needed
5. **Use the working examples** as templates for your applications

## 🔮 Future Considerations

- **Inference Profiles**: For newer models like Claude 4, you'll need to set up inference profiles
- **Bedrock Prompt Management**: When available, use the comprehensive prompt management features
- **Model Updates**: Keep track of new model releases and their requirements

## 📝 Notes

- All tests were run in `us-east-1` region
- Virtual environment was used to avoid system package conflicts
- Claude 3 Haiku provided excellent responses for all test cases
- Prompt template concept works perfectly with variable substitution
- The code is ready for production use with the working models
