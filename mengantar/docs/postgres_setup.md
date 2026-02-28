# PostgreSQL Setup Guide

## Overview

Project ini menggunakan **PostgreSQL 17** sebagai database backend:
- **On-Premise**: Deployment di data center customer dengan full control.
- **SaaS Version**: Cloud hosting untuk multi-tenant SaaS.

**PENTING**: Versi PostgreSQL **harus PostgreSQL 17** untuk memastikan kompatibilitas penuh.

---

## Quick Setup (Docker) 🐳

Setup ini direkomendasikan untuk pengembangan lokal.

1. **Docker Compose**: Service PostgreSQL sudah tersedia di root `docker-compose.yml`.
2. **Initialization**: File `backend/init-db.sql` akan otomatis membuat schema `mengantar_test` dan extension yang diperlukan saat kontainer pertama kali dijalankan.
3. **Start**:
   ```bash
   docker-compose up -d postgres
   ```

---

## Environment Configuration

Update file `backend/.env`:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/postgres
```

---

## Database Schema

Kami menggunakan schema **`mengantar_test`** untuk tabel aplikasi:
- `mengantar_test.testimonials`: Menyimpan metadata testimonial gambar.

LangGraph uses the **`mengantar_test`** schema (as configured in the search path) for table checkpointing internalnya:
- `mengantar_test.checkpoints`
- `mengantar_test.checkpoint_blobs`
- `mengantar_test.checkpoint_writes`
- `mengantar_test.checkpoint_migrations`

---

## Running Migrations (Alembic)

Kami menggunakan **Alembic** untuk manajemen skema.

### Automation
Dalam Docker, migrasi dijalankan secara otomatis saat startup backend melalui `entrypoint.sh`.

### Manual (Local Dev)
Jika Anda mengembangkan di luar Docker:

```bash
# 1. Pastikan PostgreSQL menyala
# 2. Jalankan migrasi ke versi terbaru
cd backend/
uv run alembic upgrade head
```

Lihat [Database Migration Guide](./database_migrations.md) untuk detail lebih lanjut tentang pembuatan migrasi baru.

---

## Monitoring & Maintenance

### Check active connections
```bash
psql $DATABASE_URL -c "
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';
"
```

### Check database size
```bash
psql $DATABASE_URL -c "
SELECT 
  pg_size_pretty(pg_database_size('postgres')) as database_size;
"
```
