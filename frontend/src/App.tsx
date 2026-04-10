import { useState, useEffect, useMemo, useRef } from 'react'
import './App.css'

function App() {
  const [targetItem, setTargetItem] = useState('electronic-circuit')
  const [rate, setRate] = useState(100)
  const [beltTier, setBeltTier] = useState('express-transport-belt')
  const [inserterTier, setInserterTier] = useState('fast-inserter')
  const [machineTier, setMachineTier] = useState('assembling-machine-3')
  const [poleTier, setPoleTier] = useState('medium-electric-pole')
  
  const [allItems, setAllItems] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [showDropdown, setShowDropdown] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const [responseStatus, setResponseStatus] = useState<string | null>(null)
  const [blueprint, setBlueprint] = useState<string | null>(null)
  const [entities, setEntities] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

  const ITEMS = [
    { id: 'electronic-circuit', name: 'Electronic Circuit (Green)' },
    { id: 'advanced-circuit', name: 'Advanced Circuit (Red)' },
    { id: 'processing-unit', name: 'Processing Unit (Blue)' },
    { id: 'plastic-bar', name: 'Plastic Bar' },
    { id: 'speed-module-3', name: 'Speed Module 3' },
    { id: 'productivity-module-3', name: 'Productivity Module 3' },
    { id: 'low-density-structure', name: 'Low Density Structure' },
    { id: 'rocket-control-unit', name: 'Rocket Control Unit' },
    { id: 'rocket-fuel', name: 'Rocket Fuel' },
    { id: 'iron-plate', name: 'Iron Plate' },
    { id: 'copper-plate', name: 'Copper Plate' },
    { id: 'steel-plate', name: 'Steel Plate' },
  ]

  const BELTS = [
    { id: 'transport-belt', name: 'Yellow (Standard)' },
    { id: 'fast-transport-belt', name: 'Red (Fast)' },
    { id: 'express-transport-belt', name: 'Blue (Express)' },
  ]

  const INSERTERS = [
    { id: 'inserter', name: 'Yellow (Standard)' },
    { id: 'fast-inserter', name: 'Blue (Fast)' },
    { id: 'stack-inserter', name: 'Green (Stack)' },
  ]

  const MACHINES = [
    { id: 'assembling-machine-1', name: 'Assembling Machine 1' },
    { id: 'assembling-machine-2', name: 'Assembling Machine 2' },
    { id: 'assembling-machine-3', name: 'Assembling Machine 3' },
    { id: 'chemical-plant', name: 'Chemical Plant' },
  ]

  const POLES = [
    { id: 'small-electric-pole', name: 'Small (Wood)' },
    { id: 'medium-electric-pole', name: 'Medium (Iron)' },
    { id: 'substation', name: 'Substation (High-Tech)' },
  ]

  // Carga inicial dos itens da biblioteca Draftsman
  useEffect(() => {
    // Helper para buscar ícones da Wiki Oficial do Factorio
  const getWikiIconUrl = (itemName: string) => {
    // Transforma 'express-transport-belt' em 'Express_transport_belt.png'
    const formatted = itemName
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('_');
    return `https://wiki.factorio.com/images/${formatted}.png`;
  };

  const fetchItems = async () => {
      try {
        const res = await fetch('http://127.0.0.1:8000/api/items/');
        const data = await res.json();
        setAllItems(data);
      } catch (err) {
        console.error("Failed to fetch items", err);
      }
    };
    fetchItems();
  }, []);

  // Fechar dropdown ao clicar fora
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const filteredItems = useMemo(() => {
    if (!searchQuery) return allItems.slice(0, 50); // Mostra 50 primeiros por padrão
    return allItems.filter(item => 
      item.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
      item.id.toLowerCase().includes(searchQuery.toLowerCase())
    ).slice(0, 50);
  }, [searchQuery, allItems]);

  const selectedItemName = allItems.find(i => i.id === targetItem)?.name || targetItem;

  const handleGenerate = async () => {
    setLoading(true)
    setResponseStatus(null)
    setBlueprint(null)
    setEntities([])
    
    const payload = {
      mode: "simple",
      target: targetItem,
      rate_per_minute: Number(rate),
      options: {
        tileable_block: true,
        max_machines_per_block: 15
      },
      tech_tier: {
        belt: beltTier,
        inserter: inserterTier,
        machine: machineTier,
        pole: poleTier
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
        setEntities(data.entities_map || []);
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
          
          <div className="form-grid">
            <div className="form-group search-container" ref={dropdownRef}>
              <label>Target Item:</label>
              <div className="search-input-wrapper">
                <input 
                  type="text" 
                  placeholder="Search item (e.g. circuit)..."
                  value={showDropdown ? searchQuery : selectedItemName}
                  onFocus={() => { setShowDropdown(true); setSearchQuery(''); }}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  disabled={loading}
                />
                {showDropdown && (
                  <div className="search-dropdown">
                    {filteredItems.map(item => (
                      <div 
                        key={item.id} 
                        className="dropdown-item"
                        onClick={() => {
                          setTargetItem(item.id);
                          setSearchQuery(item.name);
                          setShowDropdown(false);
                        }}
                      >
                        <img 
                          src={getWikiIconUrl(item.id)} 
                          alt="" 
                          style={{ width: '20px', height: '20px', marginRight: '10px', verticalAlign: 'middle' }}
                          onError={(e) => (e.currentTarget.style.display = 'none')}
                        />
                        {item.name}
                      </div>
                    ))}
                    {filteredItems.length === 0 && <div className="dropdown-no-results">No items found</div>}
                  </div>
                )}
              </div>
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

            <div className="form-group">
              <label>Belt Tier:</label>
              <select value={beltTier} onChange={(e) => setBeltTier(e.target.value)} disabled={loading}>
                {BELTS.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Inserter Tier:</label>
              <select value={inserterTier} onChange={(e) => setInserterTier(e.target.value)} disabled={loading}>
                {INSERTERS.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Machine Tier:</label>
              <select value={machineTier} onChange={(e) => setMachineTier(e.target.value)} disabled={loading}>
                {MACHINES.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
              </select>
            </div>

            <div className="form-group">
              <label>Power Pole Tier:</label>
              <select value={poleTier} onChange={(e) => setPoleTier(e.target.value)} disabled={loading}>
                {POLES.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
              </select>
            </div>
          </div>

          <button 
            className="btn-generate" 
            onClick={handleGenerate} 
            disabled={loading}
          >
            {loading ? 'Crunching Numbers...' : 'Generate High-Density Blueprint'}
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

          {entities.length > 0 && (
            <div className="visualizer-container">
              <h3>Blueprint Preview:</h3>
              <div className="blueprint-grid">
                {entities.map((ent: any, index: number) => {
                  const pos = ent.position;
                  const type = ent.name;
                  const scale = 20; 
                  let size = 1;
                  if (type.includes('assembling-machine')) size = 3;
                  if (type.includes('combinator')) size = 1;
                  if (type.includes('chemical-plant')) size = 3;
                  if (type.includes('splitter')) size = 2;

                  const style = {
                    left: `${(pos.x - (type.includes('splitter') ? 1 : size/2)) * scale}px`,
                    top: `${(pos.y - size/2) * scale}px`,
                    width: `${(type.includes('splitter') ? 2 : size) * scale}px`,
                    height: `${size * scale}px`,
                  };

                  let className = "grid-entity";
                  if (type.includes('assembling-machine') || type.includes('chemical-plant')) className += " machine";
                  if (type.includes('belt')) className += " belt";
                  if (type.includes('inserter')) className += " inserter";
                  if (type.includes('combinator')) className += " combinator";
                  if (type.includes('pipe')) className += " pipe";
                  if (type.includes('pole')) className += " pole";
                  if (type.includes('substation')) {
                    className += " substation";
                    size = 2; // Garantir tamanho 2x2
                  }

                  return (
                    <div 
                      key={index} 
                      className={className} 
                      style={style}
                      title={`${type} at ${pos.x}, ${pos.y}`}
                    >
                      {(type.includes('machine') || type.includes('chemical-plant') || type.includes('splitter') || type.includes('pole') || type.includes('substation')) && (
                        <img 
                          src={getWikiIconUrl(type)} 
                          alt="" 
                          style={{ width: '80%', height: '80%', opacity: 0.8 }}
                          onError={(e) => (e.currentTarget.style.display = 'none')}
                        />
                      )}
                    </div>
                  );
                })}
              </div>
            </div>
          )}

        </section>
      </main>
    </div>
  )
}

export default App
