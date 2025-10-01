# Gemini Model Configuration Guide

## Available Models

### **Gemini 1.5 Pro** (Recommended)
- **Model Name**: `gemini-1.5-pro`
- **Best for**: Complex reasoning, coding, analysis
- **Context**: 2M tokens
- **Speed**: Moderate
- **Quality**: Highest

### **Gemini 1.5 Flash** (Fast)
- **Model Name**: `gemini-1.5-flash`
- **Best for**: Quick responses, simple tasks
- **Context**: 1M tokens  
- **Speed**: Fastest
- **Quality**: Good

### **Gemini 1.0 Pro** (Stable)
- **Model Name**: `gemini-1.0-pro`
- **Best for**: General purpose, stable
- **Context**: 32K tokens
- **Speed**: Fast
- **Quality**: Good

## How to Change Models

### Method 1: Update .env file
```bash
# Edit agentContainer/.env
GEMINI_MODEL=gemini-1.5-flash  # For speed
# or
GEMINI_MODEL=gemini-1.5-pro   # For quality
```

### Method 2: Environment Variable
```powershell
# Set before running
$env:GEMINI_MODEL="gemini-1.5-flash"
.\run-app.ps1 run
```

### Method 3: Docker Compose Override
```yaml
# In docker-compose.override.yml
services:
  notebook-agent:
    environment:
      - GEMINI_MODEL=gemini-1.5-flash
```

## Testing Models

```powershell
# Test current model
.\test-credentials.ps1 -Rebuild

# Or test manually
docker-compose run --rm notebook-agent python test_models.py
```

## Performance Comparison

| Model | Speed | Quality | Context | Best For |
|-------|-------|---------|---------|----------|
| gemini-1.5-pro | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 2M | Complex notebooks, detailed analysis |
| gemini-1.5-flash | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | 1M | Quick prototypes, simple notebooks |
| gemini-1.0-pro | ⭐⭐⭐⭐ | ⭐⭐⭐ | 32K | General purpose, stable |

## Troubleshooting

### Error: Model not found
```
Error: 404 models/gemini-pro is not found
```
**Solution**: Update to correct model name in `.env`:
```bash
GEMINI_MODEL=gemini-1.5-pro  # Not "gemini-pro"
```

### Error: Quota exceeded
**Solution**: Switch to faster model temporarily:
```bash
GEMINI_MODEL=gemini-1.5-flash
```

### Error: Authentication failed
**Solution**: Check credentials:
```powershell
.\test-credentials.ps1
```