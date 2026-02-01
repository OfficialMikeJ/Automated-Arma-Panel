# Feature Requests & Roadmap

## Backup & Storage Integration Feature

### Overview
Add comprehensive backup and download capabilities with third-party cloud storage integration for admin accounts.

### Feature Details

#### 1. Backup Management
- **Database Backups**
  - Automatic MongoDB backups (scheduled)
  - Manual on-demand backups
  - Backup retention policies (keep last N backups)
  - Backup compression (tar.gz)
  
- **Server Instance Backups**
  - Full server directory backup
  - Configuration files backup
  - Mod files backup
  - Save game files backup

#### 2. Download Capabilities
- **Local Downloads**
  - Download backup files directly to admin's computer
  - Batch download multiple backups
  - Resume interrupted downloads
  
#### 3. Third-Party Storage Integration

**Supported Services:**
- ✅ Linode Object Storage
- ✅ Vultr Object Storage
- ✅ Wasabi Hot Cloud Storage
- ✅ Amazon S3
- ✅ Backblaze B2
- ✅ DigitalOcean Spaces
- ✅ Generic S3-compatible storage

**Features:**
- Auto-upload backups to cloud storage
- Restore from cloud storage
- Sync local and cloud backups
- Encryption for cloud-stored backups
- Bandwidth throttling
- Multi-destination backup (upload to multiple services)

#### 4. User Interface

**Dashboard Section:**
```
Backups & Storage
├── Local Backups
│   ├── Database Backups (list with download buttons)
│   ├── Server Backups (list with download buttons)
│   └── Create New Backup
├── Cloud Storage Settings
│   ├── Configure Linode
│   ├── Configure Vultr
│   ├── Configure Wasabi
│   └── Add Custom S3 Provider
└── Backup Schedule
    ├── Automatic Backup Schedule
    ├── Retention Policy
    └── Upload Destinations
```

**Modal Components:**
- `CloudStorageConfigModal.js` - Configure cloud providers
- `BackupManagementModal.js` - View/download/restore backups
- `BackupScheduleModal.js` - Set up automatic backups

#### 5. Backend Implementation

**New API Endpoints:**
```
POST   /api/backups/database          - Create database backup
POST   /api/backups/server/{id}       - Create server instance backup
GET    /api/backups                   - List all backups
GET    /api/backups/{id}/download     - Download backup file
DELETE /api/backups/{id}              - Delete backup
POST   /api/backups/{id}/restore      - Restore from backup

POST   /api/storage/configure         - Configure cloud storage
GET    /api/storage/providers         - List configured providers
POST   /api/storage/upload/{backup}   - Upload backup to cloud
POST   /api/storage/sync              - Sync with cloud storage
GET    /api/storage/list              - List cloud-stored backups
```

**Database Collections:**
```javascript
// backups collection
{
  _id: ObjectId,
  backup_id: string,
  type: "database" | "server",
  server_id: string (optional),
  filename: string,
  file_path: string,
  file_size_mb: number,
  created_at: datetime,
  created_by: string (user_id),
  cloud_locations: [
    {
      provider: "linode" | "vultr" | "wasabi" | "s3",
      uploaded_at: datetime,
      url: string,
      encrypted: boolean
    }
  ],
  status: "local" | "uploaded" | "archived"
}

// storage_providers collection
{
  _id: ObjectId,
  provider_id: string,
  provider_type: "linode" | "vultr" | "wasabi" | "s3" | "custom",
  name: string,
  config: {
    endpoint: string,
    bucket: string,
    region: string,
    access_key: string (encrypted),
    secret_key: string (encrypted)
  },
  enabled: boolean,
  auto_upload: boolean,
  created_at: datetime
}
```

#### 6. Technical Implementation

**Backup Creation:**
```python
# Database backup using mongodump
import subprocess
from datetime import datetime

def create_database_backup():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = f"/tmp/backups/db_{timestamp}"
    
    subprocess.run([
        "mongodump",
        "--uri", MONGO_URL,
        "--out", backup_dir
    ])
    
    # Compress
    subprocess.run([
        "tar", "-czf",
        f"{backup_dir}.tar.gz",
        backup_dir
    ])
    
    return f"{backup_dir}.tar.gz"
```

**Cloud Upload (S3-compatible):**
```python
import boto3
from botocore.client import Config

def upload_to_cloud(file_path, provider_config):
    s3_client = boto3.client(
        's3',
        endpoint_url=provider_config['endpoint'],
        aws_access_key_id=provider_config['access_key'],
        aws_secret_access_key=provider_config['secret_key'],
        config=Config(signature_version='s3v4'),
        region_name=provider_config['region']
    )
    
    with open(file_path, 'rb') as file:
        s3_client.upload_fileobj(
            file,
            provider_config['bucket'],
            os.path.basename(file_path)
        )
```

#### 7. Security Considerations

- Encrypt backup files before uploading to cloud
- Store cloud credentials encrypted in database
- Admin-only access to backup features
- Audit log for all backup operations
- Secure file downloads with temporary signed URLs
- Rate limiting on backup creation
- Size limits for backups

#### 8. Configuration Example

**Linode Object Storage:**
```
Endpoint: https://us-east-1.linodeobjects.com
Bucket: tactical-panel-backups
Region: us-east-1
Access Key: [from Linode console]
Secret Key: [from Linode console]
```

**Vultr Object Storage:**
```
Endpoint: https://ewr1.vultrobjects.com
Bucket: tactical-backups
Region: ewr1
Access Key: [from Vultr console]
Secret Key: [from Vultr console]
```

**Wasabi:**
```
Endpoint: https://s3.us-east-1.wasabisys.com
Bucket: tactical-panel
Region: us-east-1
Access Key: [from Wasabi console]
Secret Key: [from Wasabi console]
```

#### 9. Future Enhancements

- Incremental backups (only changed files)
- Backup verification (integrity checks)
- Backup encryption with custom keys
- Scheduled restore testing
- Backup analytics (size trends, frequency)
- Email notifications on backup success/failure
- Webhook notifications
- FTP/SFTP support
- Google Drive / Dropbox integration

---

## Priority & Effort

**Priority:** Medium-High (valuable QOL feature)  
**Effort:** Large (2-3 weeks development)  
**Dependencies:** 
- boto3 library for S3-compatible storage
- Encryption library (cryptography)
- Background task queue for uploads

---

## Implementation Phases

### Phase 1: Local Backups
- Database backup creation
- Server backup creation
- List and download backups
- Manual backup deletion

### Phase 2: Cloud Storage Integration
- S3-compatible provider configuration
- Upload to cloud storage
- List cloud-stored backups
- Download from cloud

### Phase 3: Automation
- Scheduled automatic backups
- Retention policies
- Auto-upload to configured providers
- Email notifications

### Phase 4: Advanced Features
- Backup encryption
- Multi-destination upload
- Restore functionality
- Backup verification

---

## User Feedback
Requested by: Admin user (Feb 1, 2025)  
Use case: Ensure data safety and disaster recovery for game servers  
Benefit: Peace of mind, easy data portability, offsite backups

---

**Status:** Documented - Ready for implementation planning
