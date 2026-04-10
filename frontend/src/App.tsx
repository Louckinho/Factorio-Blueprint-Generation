import { useState } from 'react'
import './App.css'

function App() {
  const [targetItem, setTargetItem] = useState('plastic-bar')
  const [rate, setRate] = useState(5000)
  const [responseStatus, setResponseStatus] = useState<string | null>(null)
  const [blueprint, setBlueprint] = useState<string | null>(null)
  const [loading, setLoading] = useState(false)

  const handleGenerate = async () => {
    setLoading(true)
    setResponseStatus(null)
    setBlueprint(null)
    
    const payload = {
      mode: "simple",
      target: targetItem,
      rate_per_minute: Number(rate),
      options: {
        tileable_block: true,
        max_machines_per_block: 15
      },
      tech_tier: {
        belt: "express-transport-belt",
        inserter: "fast-inserter",
        machine: "chemical-plant"
      },
      modules: {
        beaconized: true,
        beacon_entity: "beacon",
        machine_modules: ["productivity-module-3"],
        beacon_modules: ["speed-module-3"]
      }
    };

    try {
      const res = await fetch('http://127.0.0.1:8000/api/generate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });

      const data = await res.json();

      if (!res.ok) {
        setResponseStatus(`Error: ${res.status} - ${JSON.stringify(data)}`);
      } else {
        setResponseStatus(`Success! Generated blueprint for ${data.metadata.item}`);
        setBlueprint(data.blueprint_string);
      }
    } catch (err: any) {
      setResponseStatus(`Network Error: ${err.message}`);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="app-container">
      <header className="header">
        <h1>Factorio Blueprint Generator</h1>
        <span className="version-badge">v4.0 High-Density Edition</span>
      </header>

      <main className="main-content">
        <section className="config-panel">
          <h2>Blueprint Configuration</h2>
          <p>Select your mode and items below.</p>
          
          <div className="form-group">
            <label>Target Item:</label>
            <input 
              type="text" 
              value={targetItem} 
              onChange={(e) => setTargetItem(e.target.value)} 
              disabled={loading}
            />
          </div>

          <div className="form-group">
            <label>Rate / min:</label>
            <input 
              type="number" 
              value={rate} 
              onChange={(e) => setRate(Number(e.target.value))} 
              disabled={loading}
            />
          </div>

          <button 
            className="btn-generate" 
            onClick={handleGenerate} 
            disabled={loading}
          >
            {loading ? 'Routing Belts...' : 'Generate Blueprint'}
          </button>

          {responseStatus && (
            <div className={`status-box ${responseStatus.includes('Error') ? 'error' : 'success'}`}>
              {responseStatus}
            </div>
          )}

          {blueprint && (
            <div className="blueprint-box">
              <h3>Base64 Output:</h3>
              <textarea readOnly value={blueprint} />
            </div>
          )}

        </section>
      </main>
    </div>
  )
}

export default App
