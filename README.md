# n8n Docker Compose for Ogna Stack

A Docker Compose configuration for running n8n (workflow automation platform) as part of the Ogna stack.

## About n8n

n8n is a fair-code licensed workflow automation tool that allows you to connect various services and automate tasks. It's an excellent alternative to tools like Zapier or Make.

## Prerequisites

- Docker (version 20.10 or higher)
- Docker Compose (version 2.0 or higher)
- At least 2GB of available RAM

## Quick Start

1. Clone this repository:

```bash
git clone https://github.com/ognaapps/n8n.git
cd n8n
```

2. Create environment file:

```bash
cp .env.example .env
# Edit .env with your configuration
```

3. Start n8n:

```bash
docker-compose up -d
```

4. Access n8n:
   - Open your browser and navigate to `http://localhost:5678`
   - Create your initial admin account

## Configuration

### Default Settings

- **n8n Version**: Latest stable
- **Port**: 5678
- **Data Persistence**: Workflows and credentials are stored in Docker volumes
- **Timezone**: UTC (configurable)

### Environment Variables

Edit your `.env` file with the following configurations:

```bash
# Basic Configuration
N8N_PORT=5678
N8N_PROTOCOL=http
N8N_HOST=localhost

# Security (IMPORTANT: Change these!)
N8N_BASIC_AUTH_USER=admin
N8N_BASIC_AUTH_PASSWORD=changeme

# Timezone
GENERIC_TIMEZONE=America/New_York
TZ=America/New_York

# Execution
EXECUTIONS_MODE=regular
EXECUTIONS_TIMEOUT=3600
EXECUTIONS_TIMEOUT_MAX=7200

# Webhook URL (for production)
WEBHOOK_URL=https://your-domain.com/

# Database (if using external database)
DB_TYPE=postgresdb
DB_POSTGRESDB_HOST=postgres
DB_POSTGRESDB_PORT=5432
DB_POSTGRESDB_DATABASE=n8n
DB_POSTGRESDB_USER=n8n
DB_POSTGRESDB_PASSWORD=changeme
```

## Accessing n8n

### Local Development

```
http://localhost:5678
```

### Production (with domain)

```
https://your-domain.com
```

## Integration with Ogna Stack

This n8n instance is designed to work seamlessly with other Ogna stack components:

- **MongoDB**: Connect to `mongodb://mongo:27017` from workflows
- **APIs**: Trigger workflows via webhooks
- **Services**: Automate interactions between microservices

## Common Workflows

### Example: Webhook Trigger

1. Create a new workflow
2. Add a "Webhook" trigger node
3. Set the webhook path (e.g., `/webhook-test`)
4. Test URL: `http://localhost:5678/webhook-test/test`
5. Production URL: `https://your-domain.com/webhook-test/`

### Example: Schedule Trigger

1. Add a "Schedule Trigger" node
2. Set cron expression (e.g., `0 9 * * *` for daily at 9 AM)
3. Add workflow logic
4. Activate the workflow

## Management

### Start Services

```bash
docker-compose up -d
```

### Stop Services

```bash
docker-compose down
```

### View Logs

```bash
docker-compose logs -f n8n
```

### Restart Service

```bash
docker-compose restart n8n
```

### Update n8n

```bash
docker-compose pull
docker-compose up -d
```

## Data Persistence

Data is persisted in the following Docker volumes:

- `n8n_data`: Workflows, credentials, and configuration
- `n8n_files`: File storage for workflow executions

### Backup Workflows

```bash
# Export all workflows
docker-compose exec n8n n8n export:workflow --all --output=/backup/

# Copy from container
docker cp n8n_container:/backup/ ./backup/
```

### Restore Workflows

```bash
# Copy to container
docker cp ./backup/ n8n_container:/backup/

# Import workflows
docker-compose exec n8n n8n import:workflow --input=/backup/
```

## Security Best Practices

⚠️ **Critical Security Steps**:

1. **Change Default Credentials**

   - Update `N8N_BASIC_AUTH_USER` and `N8N_BASIC_AUTH_PASSWORD`
   - Never use default credentials in production

2. **Use HTTPS in Production**

   - Configure SSL/TLS certificates
   - Set `N8N_PROTOCOL=https`
   - Update `WEBHOOK_URL` to use https

3. **Secure Webhook URLs**

   - Use authentication for webhook endpoints
   - Implement IP whitelisting if possible

4. **Credentials Management**

   - n8n encrypts credentials by default
   - Set encryption key: `N8N_ENCRYPTION_KEY=your-secret-key`
   - Keep this key secure and backed up

5. **Network Security**
   - Use Docker networks to isolate services
   - Don't expose n8n directly to the internet without reverse proxy

## Reverse Proxy Setup (nginx)

Example nginx configuration:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5678;
        proxy_set_header Connection '';
        proxy_http_version 1.1;
        chunked_transfer_encoding off;
        proxy_buffering off;
        proxy_cache off;
    }
}
```

## Troubleshooting

### n8n Won't Start

- Check logs: `docker-compose logs n8n`
- Verify port 5678 is available: `lsof -i :5678`
- Check environment variables in `.env`

### Workflows Not Executing

- Check execution mode: Should be `regular` for standard deployment
- Verify timeout settings
- Check workflow activation status
- Review execution logs in n8n UI

### Webhook Not Responding

- Verify `WEBHOOK_URL` is correctly set
- Check firewall/port forwarding
- Test webhook with curl:
  ```bash
  curl -X POST http://localhost:5678/webhook-test/test
  ```

### Database Connection Issues

- Verify database is running
- Check connection credentials
- Ensure database is accessible from n8n container

### Permission Errors

- Check volume permissions
- Ensure Docker has write access to volume directories

## Development Tips

### Testing Workflows

- Use the "Execute Workflow" button for manual testing
- Enable "Always Output Data" in node settings
- Use "Webhook" node test URLs during development

### Debugging

- Enable verbose logging: `N8N_LOG_LEVEL=debug`
- Check execution data in the UI
- Use "Error Trigger" nodes to catch failures

## Useful n8n Features

- **Webhooks**: Trigger workflows via HTTP requests
- **Cron Jobs**: Schedule recurring workflows
- **Sub-workflows**: Reuse workflow logic
- **Error Handling**: Built-in error workflows
- **API Access**: n8n REST API for automation

## Resources

- [n8n Documentation](https://docs.n8n.io/)
- [n8n Community Forum](https://community.n8n.io/)
- [Workflow Templates](https://n8n.io/workflows/)
- [Node Documentation](https://docs.n8n.io/integrations/builtin/app-nodes/)

## License

[Specify your license]

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## Support

For issues and questions:

- Open an issue on [GitHub](https://github.com/ognaapps/n8n/issues)
- Contact the Ogna team
- Check [n8n documentation](https://docs.n8n.io/)

---

Made with ❤️ by the Ogna team
