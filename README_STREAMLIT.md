# NUSARA Mining Inference - Streamlit Dashboard

Interactive web dashboard untuk testing dan visualisasi API predictions dari NUSARA Mining Inference API.

## Features

### 📊 Dashboard Pages

1. **Overview** - API status, available endpoints, dan dokumentasi
2. **Equipment Failure** - Prediksi risiko kegagalan alat berat
3. **Maintenance Priority** - Prioritas maintenance untuk equipment
4. **Cost Anomaly** - Deteksi anomali biaya menggunakan Isolation Forest
5. **What-If Simulation** - Simulasi skenario produksi
6. **Full Pipeline** - Run semua model sekaligus dengan executive summary
7. **Custom Input** - Input data manual untuk testing

### 🎨 Visualizations

- Risk level distribution charts
- Maintenance priority pie charts
- Cost anomaly variance charts
- What-if scenario comparisons
- Interactive data tables
- Real-time metrics and KPIs

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements_streamlit.txt
```

Dependencies yang dibutuhkan:
- streamlit >= 1.32.0
- requests >= 2.31.0
- pandas >= 2.0.0
- plotly >= 5.18.0

### 2. Verify API Endpoint

Pastikan API sudah running di:
```
https://herutriana44-ai-nusara-mining-api.hf.space/
```

Check API health:
```bash
curl https://herutriana44-ai-nusara-mining-api.hf.space/health
```

## Usage

### Start the Dashboard

```bash
streamlit run streamlit_app.py
```

atau gunakan launcher script:

```bash
chmod +x run_streamlit.sh
./run_streamlit.sh
```

Dashboard akan terbuka di browser pada `http://localhost:8501`

### Using the Dashboard

#### 1. Sidebar Configuration

- **API Key**: Optional, masukkan jika API menggunakan authentication
- **API Status Check**: Klik "Check API Health" untuk verify koneksi
- **Navigation**: Pilih page yang ingin diakses

#### 2. Running Predictions

**Opsi A: Menggunakan Data Default (Bundled CSV)**

Cukup klik tombol "Run..." pada halaman yang dipilih. API akan menggunakan data dari `ml_datasets/`.

**Opsi B: Menggunakan Custom Data**

1. Pilih halaman "Custom Input"
2. Isi form sesuai jenis data (Equipment/Financial/Production)
3. Tambahkan multiple records jika diperlukan
4. Klik "Run Predictions with Custom Data"

#### 3. Viewing Results

- **Metrics Cards**: Summary statistics di bagian atas
- **Charts**: Interactive visualizations menggunakan Plotly
- **Tables**: Detail predictions dalam format tabel
- **Expandable Sections**: Klik untuk melihat detail lengkap
- **JSON Output**: Raw JSON response dari API

### Example Workflows

#### Workflow 1: Quick Health Check

1. Buka dashboard
2. Sidebar → "Check API Health"
3. Verify status = "ok" dan models loaded > 0

#### Workflow 2: Equipment Risk Assessment

1. Pilih "Equipment Failure" page
2. Klik "Run Equipment Failure Prediction"
3. Review metrics: High Risk, Medium Risk, Low Risk
4. Check "Top 5 Highest Risk Equipment" table
5. Plan maintenance untuk high-risk equipment

#### Workflow 3: Full Analysis

1. Pilih "Full Pipeline" page
2. Klik "Run Full Pipeline"
3. Review Executive Summary dengan recommendations
4. Explore detail di setiap tab:
   - Equipment Failure
   - Maintenance Priority
   - Cost Anomaly
   - What-If Simulation
5. Export/save JSON output jika diperlukan

#### Workflow 4: Custom Data Testing

1. Pilih "Custom Input" page
2. Tab "Equipment Data" → Isi form
3. Tambahkan multiple records (optional)
4. Klik "Run Predictions with Custom Data"
5. View results di tabs yang muncul

## API Configuration

### Base URL

Default: `https://herutriana44-ai-nusara-mining-api.hf.space`

Untuk mengubah API endpoint, edit di `streamlit_app.py`:

```python
API_BASE_URL = "https://your-custom-api-url.com"
```

### API Authentication

Jika API menggunakan `X-API-Key` header:

1. Set environment variable `API_KEY` di server API
2. Input API key di sidebar dashboard
3. Semua POST requests akan include header authentication

Tanpa API key, endpoint tetap bisa diakses jika API tidak enforce authentication.

## Troubleshooting

### API Connection Failed

```
Error: API Error: HTTPSConnectionPool...
```

**Solutions:**
- Verify API URL masih aktif
- Check internet connection
- Try accessing API docs: `{API_URL}/docs`
- Check if HuggingFace Space sedang sleeping (cold start)

### No Models Loaded

```
Models Loaded: 0
```

**Solutions:**
- API mungkin belum selesai load models
- Check API logs di HuggingFace Space
- Verify folder `models/` berisi file .pkl
- Restart HuggingFace Space

### Empty Predictions

```
status: "no_input"
```

**Solutions:**
- Verify folder `ml_datasets/` berisi CSV files
- Check CSV structure match expected features
- Try custom input dengan manual data

### Slow Response

**Causes:**
- HuggingFace Space cold start (first request setelah idle)
- Large dataset processing
- Network latency

**Solutions:**
- Wait 30-60 detik untuk cold start
- Use "Run Full Pipeline" hanya saat diperlukan
- Consider caching via `@st.cache_data` (sudah implemented)

## Data Format

### Equipment Data

```json
{
  "records": [{
    "date": "2025-05-01",
    "site_name": "Tambang Nikel E",
    "equipment_name": "Bulldozer BD-002",
    "equipment_type": "Bulldozer",
    "operating_hours": 286.0,
    "downtime_hours": 23.0,
    "fuel_consumption": 1667.0,
    "maintenance_cost": 849403.0
  }]
}
```

### Financial Data

```json
{
  "records": [{
    "date": "2022-01-02",
    "site_name": "Area Tambang C",
    "project_name": "Project Alpha",
    "budgeted_cost": 171870.0,
    "actual_cost": 127873.0
  }]
}
```

### Production Data

```json
{
  "records": [{
    "date": "2025-05-02",
    "site_name": "Area Tambang C",
    "material_name": "Iron",
    "produced_volume": 56.0,
    "unit_cost": 161.0
  }]
}
```

## Customization

### Styling

Edit CSS di bagian `st.markdown()` dalam `streamlit_app.py`:

```python
st.markdown("""
    <style>
    .main-header { ... }
    .metric-card { ... }
    </style>
""", unsafe_allow_html=True)
```

### Add New Visualizations

```python
def create_custom_chart(data):
    fig = go.Figure(...)
    return fig

st.plotly_chart(create_custom_chart(predictions))
```

### Add New Pages

```python
elif page == "New Page":
    st.header("New Feature")
    # Your code here
```

## Performance Tips

1. **Caching**: API responses di-cache 5 menit (`ttl=300`)
2. **Parallel API Calls**: Multiple endpoints bisa dipanggil parallel
3. **Lazy Loading**: Charts hanya render saat page aktif
4. **Pagination**: Large tables auto-paginated oleh Streamlit

## Development Mode

Run dengan auto-reload:

```bash
streamlit run streamlit_app.py --server.runOnSave true
```

Debug mode:

```bash
streamlit run streamlit_app.py --logger.level debug
```

## Deployment

### Deploy to Streamlit Cloud

1. Push code ke GitHub repository
2. Connect repository di [share.streamlit.io](https://share.streamlit.io)
3. Set `streamlit_app.py` sebagai entrypoint
4. Add secrets jika perlu (API_KEY)
5. Deploy!

### Deploy with Docker

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY requirements_streamlit.txt .
RUN pip install -r requirements_streamlit.txt

COPY streamlit_app.py .

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

Build and run:

```bash
docker build -t nusara-streamlit .
docker run -p 8501:8501 nusara-streamlit
```

## License

Same as parent project

## Support

- API Issues: Check HuggingFace Space logs
- Dashboard Issues: Check Streamlit logs
- Feature Requests: Open issue in repository

---

Built with Streamlit for NUSARA Mining ML Inference API
