# Azure Carbon Optimization API Setup

Test if this is acutally needed!!!


## Prerequisites

1. **Enable the Carbon Optimization preview feature** (required once per tenant):

   ```bash
   az feature register --namespace Microsoft.Carbon --name DefaultFeature
   ```

   Wait until it shows `"Registered"`:

   ```bash
   az feature show --namespace Microsoft.Carbon --name DefaultFeature --query properties.state
   ```

2. **Register the Microsoft.Carbon resource provider** (required once per subscription, re-run after feature registration):

   ```bash
   az provider register --namespace Microsoft.Carbon
   ```

   Check registration status:

   ```bash
   az provider show --namespace Microsoft.Carbon --query registrationState
   ```

   Wait until it returns `"Registered"` before proceeding.

3. **Authenticate** via Azure CLI:

   ```bash
   az login
   ```

## Usage

Run the carbon emissions crawler:

```bash
python azure/crawl_azure.py
```
