import './App.css'

function App() {
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
          {/* Placeholder for the React form that will hit our Django DRF API */}
          <div className="status-box">
            Status: React Frontend Ready!
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
