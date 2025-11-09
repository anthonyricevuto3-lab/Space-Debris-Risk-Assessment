targetScope = 'resourceGroup'

@minLength(1)
@maxLength(64)
@description('Name of the environment that can be used as part of naming resource convention')
param environmentName string

@minLength(1)
@description('Primary location for all resources')
param location string

@description('Resource name prefix for all resources')
var resourceToken = uniqueString(subscription().id, resourceGroup().id, location, environmentName)

// User-Assigned Managed Identity
resource userAssignedIdentity 'Microsoft.ManagedIdentity/userAssignedIdentities@2023-01-31' = {
  name: 'azid${resourceToken}'
  location: location
}

// Log Analytics Workspace
resource logAnalyticsWorkspace 'Microsoft.OperationalInsights/workspaces@2022-10-01' = {
  name: 'azlaw${resourceToken}'
  location: location
  properties: {
    sku: {
      name: 'PerGB2018'
    }
    retentionInDays: 30
    features: {
      searchVersion: 1
      legacy: 0
      enableLogAccessUsingOnlyResourcePermissions: true
    }
  }
}

// Application Insights - Reference existing one from Azure ML workspace
resource applicationInsights 'Microsoft.Insights/components@2020-02-02' existing = {
  name: 'spacedebrisris9066306514'
}

// App Service Plan
resource appServicePlan 'Microsoft.Web/serverfarms@2023-01-01' = {
  name: 'azasp${resourceToken}'
  location: location
  sku: {
    name: 'B1'
    tier: 'Basic'
    size: 'B1'
    family: 'B'
    capacity: 1
  }
  properties: {
    reserved: true // Required for Linux
  }
  kind: 'linux'
}

// App Service
resource appService 'Microsoft.Web/sites@2023-01-01' = {
  name: 'azapp${resourceToken}'
  location: location
  tags: {
    'azd-service-name': 'web'
  }
  identity: {
    type: 'UserAssigned'
    userAssignedIdentities: {
      '${userAssignedIdentity.id}': {}
    }
  }
  properties: {
    serverFarmId: appServicePlan.id
    httpsOnly: true
    siteConfig: {
      linuxFxVersion: 'PYTHON|3.11'
      pythonVersion: '3.11'
      appCommandLine: 'gunicorn main:app'
      appSettings: [
        {
          name: 'APPLICATIONINSIGHTS_CONNECTION_STRING'
          value: applicationInsights.properties.ConnectionString
        }
        {
          name: 'ApplicationInsightsAgent_EXTENSION_VERSION'
          value: '~3'
        }
        {
          name: 'FLASK_ENV'
          value: 'production'
        }
        {
          name: 'PYTHONPATH'
          value: '/home/site/wwwroot'
        }
        {
          name: 'SCM_DO_BUILD_DURING_DEPLOYMENT'
          value: 'true'
        }
        {
          name: 'AZURE_ML_WORKSPACE_NAME'
          value: 'Space-Debris-Risk-Assessment'
        }
        {
          name: 'AZURE_ML_RESOURCE_GROUP'
          value: 'Space-Debris-Risk-Assessment-RG'
        }
        {
          name: 'AZURE_ML_SUBSCRIPTION_ID'
          value: '8d1e82fa-4fb3-48ee-99a2-b3f5784287a2'
        }
      ]
      cors: {
        allowedOrigins: ['*']
        supportCredentials: false
      }
      minTlsVersion: '1.2'
      ftpsState: 'Disabled'
    }
  }
}

// Diagnostic Settings for App Service
resource appServiceDiagnosticSettings 'Microsoft.Insights/diagnosticSettings@2021-05-01-preview' = {
  name: 'appServiceDiagnostics'
  scope: appService
  properties: {
    workspaceId: logAnalyticsWorkspace.id
    logs: [
      {
        categoryGroup: 'allLogs'
        enabled: true
      }
    ]
    metrics: [
      {
        category: 'AllMetrics'
        enabled: true
      }
    ]
  }
}

// Outputs
output AZURE_LOCATION string = location
output AZURE_TENANT_ID string = tenant().tenantId
output AZURE_RESOURCE_GROUP_ID string = resourceGroup().id

output SERVICE_WEB_IDENTITY_PRINCIPAL_ID string = userAssignedIdentity.properties.principalId
output SERVICE_WEB_NAME string = appService.name
output SERVICE_WEB_URI string = 'https://${appService.properties.defaultHostName}'
output APPLICATIONINSIGHTS_CONNECTION_STRING string = applicationInsights.properties.ConnectionString
output AZURE_LOG_ANALYTICS_WORKSPACE_NAME string = logAnalyticsWorkspace.name