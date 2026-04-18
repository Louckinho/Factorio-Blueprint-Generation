import { useState, useEffect, useMemo } from 'react'
import './App.css'

// Categories for Factorio items
const CATEGORIES = [
  { id: 'logistics', name: 'Logistics', icon: '📦', keywords: ['belt', 'underground', 'splitter', 'chest', 'pipe', 'pump', 'tank', 'robot', 'port', 'train', 'rail', 'station', 'loader', 'inserter'] },
  { id: 'production', name: 'Production', icon: '🏭', keywords: ['machine', 'furnace', 'miner', 'pumpjack', 'beacon', 'module', 'lab', 'drill'] },
  { id: 'energy', name: 'Energy', icon: '⚡', keywords: ['pole', 'substation', 'solar', 'boiler', 'steam', 'turbine', 'reactor', 'accumulator'] },
  { id: 'resources', name: 'Resources', icon: '💎', keywords: ['plate', 'steel', 'plastic', 'sulfur', 'battery', 'carbon', 'coal', 'ore', 'stone', 'brick', 'wood'] },
  { id: 'military', name: 'Military', icon: '🛡️', keywords: ['wall', 'gate', 'turret', 'radar', 'artillery', 'ammo', 'rocket', 'tank-cannon', 'gun', 'capsule'] },
  { id: 'intermediate', name: 'Intermediates', icon: '🔧', keywords: ['circuit', 'unit', 'pack', 'rocket-part', 'satellite', 'fuel', 'barrel', 'gear', 'stick'] },
]

function App() {
  const [targetItem, setTargetItem] = useState('electronic-circuit')
  const [rate, setRate] = useState(100)
  const [beltTier, setBeltTier] = useState('express-transport-belt')
  const [inserterTier, setInserterTier] = useState('fast-inserter')
  const [machineTier, setMachineTier] = useState('assembling-machine-3')
  const [poleTier, setPoleTier] = useState('medium-electric-pole')
  
  const [allItems, setAllItems] = useState<any[]>([])
  const [searchQuery, setSearchQuery] = useState('')
  const [openCategories, setOpenCategories] = useState<Record<string, boolean>>({
    'logistics': true,
    'production': true,
    'energy': true,
    'resources': true,
    'military': true,
    'intermediate': true,
    'other': true
  })

  const [responseStatus, setResponseStatus] = useState<string | null>(null)
  const [blueprint, setBlueprint] = useState<string | null>(null)
  const [entities, setEntities] = useState<any[]>([])
  const [loading, setLoading] = useState(false)

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

  const getIconUrl = (itemId: string) => {
    if (!itemId) return "";
    return `/icons/${itemId}.png`;
  };

  const getBaseIconUrl = (itemId: string) => {
    if (!itemId) return "";
    const baseId = itemId.replace(/-recycling$|-crushing$|-processing$|-separation$|-neutralisation$|-cracking$|-liquefaction$|-cleaning$/g, '');
    return `/icons/${baseId}.png`;
  };

  const getWikiFallbackUrl = (itemName: string) => {
    if (!itemName) return "";
    const formatted = itemName
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join('_');
    return `https://wiki.factorio.com/images/${formatted}.png`;
  };

  useEffect(() => {
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

  const categorizedItems = useMemo(() => {
    const groups: Record<string, any[]> = {
      'logistics': [],
      'production': [],
      'energy': [],
      'resources': [],
      'military': [],
      'intermediate': [],
      'other': []
    };

    // Filter out unwanted items (recycling, admin, technical, duplicates)
    const filtered = allItems.filter(item => {
      const id = item.id;
      
      // Exclude technical/sandbox items
      if (id.startsWith('infinity-') || id.startsWith('editor-') || id.includes('parameter-') || id.includes('planner') || id.includes('blueprint') || id.startsWith('selection-tool')) return false;
      if (id.includes('simple-entity') || id.includes('dummy-') || id.includes('loader')) return false;
      
      // Exclude secondary recipe variants (recycling, etc)
      if (id.endsWith('-recycling') || id.includes('-reprocessing') || id.includes('-crushing')) return false;
      
      // Applied search query
      if (searchQuery && !item.name.toLowerCase().includes(searchQuery.toLowerCase()) && !id.toLowerCase().includes(searchQuery.toLowerCase())) {
        return false;
      }
      
      return true;
    });

    filtered.forEach(item => {
      let found = false;
      for (const cat of CATEGORIES) {
        if (cat.keywords.some(kw => item.id.includes(kw))) {
          groups[cat.id].push(item);
          found = true;
          break;
        }
      }
      if (!found) groups['other'].push(item);
    });

    return groups;
  }, [allItems, searchQuery]);

  const selectedItem = useMemo(() => {
    const item = allItems.find(i => i.id === targetItem);
    if (item) return item;
    
    // Fallback formatting if item not found in list yet
    const displayName = targetItem
      .split('-')
      .map(word => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
      
    return { id: targetItem, name: displayName };
  }, [targetItem, allItems]);

  const toggleCategory = (id: string) => {
    setOpenCategories(prev => ({ ...prev, [id]: !prev[id] }));
  };

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
        headers: { 'Content-Type': 'application/json' },
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
      <aside className="sidebar">
        <div className="sidebar-header">
          <h2>Item Browser</h2>
          <div className="sidebar-search">
            <span className="search-icon">🔍</span>
            <input 
              type="text" 
              placeholder="Search items..." 
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
          </div>
        </div>
        
        <div className="sidebar-content">
          {[...CATEGORIES, { id: 'other', name: 'Other', icon: '📦' }].map(cat => {
            const items = categorizedItems[cat.id];
            if (items.length === 0 && searchQuery) return null;
            
            const isOpen = openCategories[cat.id];
            
            return (
              <div key={cat.id} className="category-group">
                <div className="category-header" onClick={() => toggleCategory(cat.id)}>
                  <div className="category-title">
                    <span>{cat.icon}</span>
                    {cat.name}
                    <span style={{ fontSize: '0.8rem', opacity: 0.5 }}>({items.length})</span>
                  </div>
                  <span className={`category-chevron ${isOpen ? 'open' : ''}`}>▼</span>
                </div>
                
                {isOpen && (
                  <div className="item-grid">
                    {items.map(item => (
                      <div 
                        key={item.id} 
                        className={`item-card ${targetItem === item.id ? 'selected' : ''}`}
                        onClick={() => setTargetItem(item.id)}
                        title={item.name}
                      >
                        <img 
                          src={getIconUrl(item.id)} 
                          alt={item.name} 
                          onError={(e) => {
                            const target = e.currentTarget;
                            if (target.src.includes(item.id) && !target.dataset.triedBase) {
                              target.dataset.triedBase = "true";
                              target.src = getBaseIconUrl(item.id);
                            } else {
                              target.src = getWikiFallbackUrl(item.id);
                              target.onerror = (evt) => (evt.currentTarget.style.display = 'none');
                            }
                          }}
                        />
                        <div className="item-tooltip">{item.name}</div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            );
          })}
        </div>
      </aside>

      <main className="main-view">
        <header className="header">
          <h1>Factorio Blueprint Generator</h1>
          <span className="version-badge">v5.0 Premium UI</span>
        </header>

        <section className="config-area">
          <div className="selected-item-box">
            <div className="selected-item-icon">
              <img 
                src={getIconUrl(targetItem)} 
                alt="" 
                onError={(e) => {
                  const target = e.currentTarget;
                  if (target.src.includes(targetItem) && !target.dataset.triedBase) {
                    target.dataset.triedBase = "true";
                    target.src = getBaseIconUrl(targetItem);
                  } else {
                    target.src = getWikiFallbackUrl(targetItem);
                    target.onerror = (evt) => (evt.currentTarget.style.display = 'none');
                  }
                }} 
              />
            </div>
            <div className="selected-item-info">
              <span className="selected-item-badge">Active Selection</span>
              <h3>{selectedItem.name}</h3>
              <p>ID: <code>{targetItem}</code></p>
            </div>
            <button 
              className="btn-generate" 
              style={{ width: 'auto', marginTop: 0, padding: '0.75rem 2rem' }}
              onClick={handleGenerate} 
              disabled={loading}
            >
              {loading ? 'Generating...' : 'Build Blueprint'}
            </button>
          </div>

          <div className="config-panel">
            <div className="form-grid">
              <div className="form-group">
                <label>Production Rate / min:</label>
                <input 
                  type="number" 
                  value={rate} 
                  onChange={(e) => setRate(Number(e.target.value))} 
                  disabled={loading}
                />
              </div>

              <div className="form-group">
                <label>Belt Quality:</label>
                <select value={beltTier} onChange={(e) => setBeltTier(e.target.value)} disabled={loading}>
                  {BELTS.map(b => <option key={b.id} value={b.id}>{b.name}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label>Inserter Strategy:</label>
                <select value={inserterTier} onChange={(e) => setInserterTier(e.target.value)} disabled={loading}>
                  {INSERTERS.map(i => <option key={i.id} value={i.id}>{i.name}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label>Machine Standard:</label>
                <select value={machineTier} onChange={(e) => setMachineTier(e.target.value)} disabled={loading}>
                  {MACHINES.map(m => <option key={m.id} value={m.id}>{m.name}</option>)}
                </select>
              </div>

              <div className="form-group">
                <label>Power Infrastructure:</label>
                <select value={poleTier} onChange={(e) => setPoleTier(e.target.value)} disabled={loading}>
                  {POLES.map(p => <option key={p.id} value={p.id}>{p.name}</option>)}
                </select>
              </div>
            </div>

            {responseStatus && (
              <div className={`status-box ${responseStatus.includes('Error') ? 'error' : 'success'}`}>
                {responseStatus}
              </div>
            )}

            {blueprint && (
              <div className="blueprint-box">
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '0.5rem' }}>
                  <h3>Blueprint Output:</h3>
                  <button 
                    onClick={() => navigator.clipboard.writeText(blueprint)}
                    style={{ background: 'transparent', border: '1px solid #22c55e', color: '#22c55e', padding: '0.2rem 0.5rem', borderRadius: '4px', cursor: 'pointer' }}
                  >
                    Copy to Clipboard
                  </button>
                </div>
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
                    if (!pos || !type) return null;
                    
                    const scale = 20; 
                    let size = 1;
                    if (type.includes('assembling-machine')) size = 3;
                    if (type.includes('chemical-plant')) size = 3;
                    if (type.includes('splitter')) size = 2;
                    if (type.includes('substation')) size = 2;

                    const style = {
                      left: `${(pos.x - (type.includes('splitter') ? 1 : size/2)) * scale}px`,
                      top: `${(pos.y - size/2) * scale}px`,
                      width: `${(type.includes('splitter') ? 2 : size) * scale}px`,
                      height: `${size * scale}px`,
                    };

                    let className = "grid-entity";
                    if (type.includes('machine') || type.includes('chemical-plant')) className += " machine";
                    if (type.includes('belt')) className += " belt";
                    if (type.includes('inserter')) className += " inserter";
                    if (type.includes('pole') || type.includes('substation')) className += " pole";

                    return (
                      <div 
                        key={index} 
                        className={className} 
                        style={style}
                        title={`${type} at ${pos.x}, ${pos.y}`}
                      >
                        {(size >= 2 || type.includes('pole')) && (
                          <img 
                            src={getIconUrl(type)} 
                            alt="" 
                            style={{ width: '80%', height: '80%', opacity: 0.8 }}
                            onError={(e) => {
                              const target = e.currentTarget;
                              if (target.src.includes(type) && !target.dataset.triedBase) {
                                target.dataset.triedBase = "true";
                                target.src = getBaseIconUrl(type);
                              } else {
                                target.src = getWikiFallbackUrl(type);
                                target.onerror = (evt) => (evt.currentTarget.style.display = 'none');
                              }
                            }}
                          />
                        )}
                      </div>
                    );
                  })}
                </div>
              </div>
            )}
          </div>
        </section>
      </main>
    </div>
  )
}

export default App
