import React, { useState } from 'react';

const ArquitecturaVoicebot = () => {
  const [activeLayer, setActiveLayer] = useState(null);
  const [activeTab, setActiveTab] = useState('arquitectura');
  
  const layers = [
    {
      id: 'data',
      name: '📊 Capa de Datos',
      color: '#3B82F6',
      components: ['Core Bancario', 'Archivo CTI', 'Centrales Riesgo', 'Data Lake'],
      description: 'Fuentes de datos y almacenamiento centralizado'
    },
    {
      id: 'ml',
      name: '🧠 Capa de Inteligencia (ML)',
      color: '#8B5CF6',
      components: ['Feature Engineering', 'Modelo Prob. Pago', 'Modelo Contactabilidad', 'Modelo Mejor Hora', 'Modelo Receptividad', 'Segmentación'],
      description: 'Modelos XGBoost para scoring y predicción'
    },
    {
      id: 'decision',
      name: '⚙️ Motor de Decisión',
      color: '#EC4899',
      components: ['Reglas de Negocio', 'Orquestador', 'CTI Enriquecido', 'Personalización'],
      description: 'Combina ML + reglas para decisiones finales'
    },
    {
      id: 'execution',
      name: '📞 Capa de Ejecución',
      color: '#10B981',
      components: ['Voicebot (Piloto)', 'Seguimiento IA', 'Call Center', 'Captura Resultados'],
      description: 'Canales de contacto y captura de resultados'
    },
    {
      id: 'observability',
      name: '📈 Observabilidad',
      color: '#F59E0B',
      components: ['Dashboard Operativo', 'Dashboard Analítico', 'Validación ML', 'Feedback Loop'],
      description: 'Monitoreo, métricas y mejora continua'
    }
  ];

  const flowSteps = [
    { time: '05:00', action: 'Extracción CTI', owner: 'Banco', icon: '📤' },
    { time: '06:00', action: 'Feature Engineering', owner: 'ML', icon: '🔧' },
    { time: '06:30', action: 'Scoring XGBoost', owner: 'ML', icon: '🧠' },
    { time: '07:00', action: 'Motor de Decisión', owner: 'ML', icon: '⚙️' },
    { time: '07:30', action: 'CTI Enriquecido', owner: 'ML', icon: '📋' },
    { time: '08-20h', action: 'Ejecución Voicebot', owner: 'Bot', icon: '📞' },
    { time: '21:00', action: 'Resultados', owner: 'Bot', icon: '📊' },
    { time: '22:00', action: 'Feedback Loop', owner: 'ML', icon: '🔄' }
  ];

  const techStack = [
    { category: 'Infraestructura', techs: ['Azure AKS', 'Data Lake', 'Azure ML'], color: '#3B82F6' },
    { category: 'Data', techs: ['Spark', 'PostgreSQL', 'Redis'], color: '#10B981' },
    { category: 'ML/AI', techs: ['XGBoost', 'MLflow', 'SHAP'], color: '#8B5CF6' },
    { category: 'Backend', techs: ['Python', 'FastAPI', 'Celery'], color: '#EC4899' },
    { category: 'Monitor', techs: ['Prometheus', 'Grafana', 'ELK'], color: '#F59E0B' }
  ];

  const models = [
    { name: 'Probabilidad de Pago', output: '0-100%', inputs: ['Hist. pagos', 'Días mora', 'Capacidad'], color: '#3B82F6', icon: '💰' },
    { name: 'Contactabilidad', output: '0-100%', inputs: ['Teléfonos', 'Intentos', 'Horarios'], color: '#8B5CF6', icon: '📱' },
    { name: 'Mejor Hora', output: 'Horario', inputs: ['Patrones', 'Ocupación', 'Historial'], color: '#EC4899', icon: '⏰' },
    { name: 'Receptividad Bot', output: '0-100%', inputs: ['Edad', 'Digital', 'Hist. bot'], color: '#10B981', icon: '🤖' }
  ];

  const segments = [
    { id: 'A', name: 'Voicebot Prioritario', criteria: 'prob≥50%, recept≥60%', color: '#10B981', action: 'Llamar primero', icon: '🟢' },
    { id: 'B', name: 'Voicebot + Seguimiento', criteria: 'prob≥30%, recept≥40%', color: '#3B82F6', action: 'Llamar + reforzar', icon: '🟡' },
    { id: 'C', name: 'Derivar a Humano', criteria: 'recept<40% o monto>$10M', color: '#F59E0B', action: 'Agente humano', icon: '🟠' },
    { id: 'D', name: 'No Gestionar Hoy', criteria: 'prob<10%, contacto<20%', color: '#EF4444', action: 'Ahorro de costo', icon: '🔴' }
  ];

  const kpis = [
    { metric: 'Contactabilidad', value: '+25%', desc: 'Mejor hora', icon: '📞' },
    { metric: 'Aceptación', value: '+30%', desc: 'Orden óptimo', icon: '✅' },
    { metric: 'Costo', value: '-35%', desc: 'Filtrar seg. D', icon: '💰' },
    { metric: 'Cumplimiento', value: '100%', desc: 'Ley 2300', icon: '⚖️' },
    { metric: 'Eficiencia', value: '+20%', desc: 'Priorización', icon: '📈' }
  ];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 text-white p-4">
      {/* Header */}
      <div className="text-center mb-6">
        <h1 className="text-2xl font-bold mb-1">🏦 Arquitectura de Producto</h1>
        <h2 className="text-lg text-blue-400">Inteligencia para Voicebot de Cobranzas</h2>
        <p className="text-gray-400 text-sm">Banco de Bogotá</p>
      </div>

      {/* Tabs */}
      <div className="flex justify-center mb-6">
        <div className="bg-gray-800 rounded-lg p-1 flex space-x-1">
          {[
            { id: 'arquitectura', label: '🏗️ Arquitectura' },
            { id: 'modelos', label: '🧠 Modelos ML' },
            { id: 'flujo', label: '⏱️ Flujo' },
            { id: 'impacto', label: '📊 Impacto' }
          ].map(tab => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-all ${
                activeTab === tab.id 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-white hover:bg-gray-700'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Tab Content */}
      {activeTab === 'arquitectura' && (
        <div className="space-y-4">
          {/* Architecture Layers */}
          <div className="bg-gray-800 rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 text-center">Arquitectura por Capas</h3>
            <div className="space-y-2">
              {layers.map((layer) => (
                <div
                  key={layer.id}
                  className={`rounded-lg p-3 cursor-pointer transition-all duration-300 ${
                    activeLayer === layer.id ? 'ring-2 ring-white' : 'hover:opacity-90'
                  }`}
                  style={{ backgroundColor: layer.color + '20', borderLeft: `4px solid ${layer.color}` }}
                  onClick={() => setActiveLayer(activeLayer === layer.id ? null : layer.id)}
                >
                  <div className="flex items-center justify-between">
                    <div>
                      <span className="font-semibold" style={{ color: layer.color }}>{layer.name}</span>
                      <p className="text-xs text-gray-400 mt-1">{layer.description}</p>
                    </div>
                    <div className="text-lg">{activeLayer === layer.id ? '▼' : '▶'}</div>
                  </div>
                  
                  {activeLayer === layer.id && (
                    <div className="mt-3 flex flex-wrap gap-2">
                      {layer.components.map((comp, i) => (
                        <div key={i} className="bg-gray-700 rounded px-2 py-1 text-xs">
                          {comp}
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>

          {/* Tech Stack */}
          <div className="bg-gray-800 rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-3">🛠️ Stack Tecnológico</h3>
            <div className="grid grid-cols-5 gap-2">
              {techStack.map((cat, index) => (
                <div key={index} className="text-center">
                  <div className="text-xs font-medium mb-2" style={{ color: cat.color }}>{cat.category}</div>
                  <div className="space-y-1">
                    {cat.techs.map((tech, i) => (
                      <div key={i} className="bg-gray-700 rounded px-2 py-1 text-xs">{tech}</div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'modelos' && (
        <div className="space-y-4">
          {/* XGBoost Models */}
          <div className="bg-gray-800 rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 text-center">Modelos XGBoost</h3>
            <div className="grid grid-cols-2 gap-3">
              {models.map((model, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-3" style={{ borderTop: `3px solid ${model.color}` }}>
                  <div className="flex items-center gap-2 mb-2">
                    <span className="text-xl">{model.icon}</span>
                    <span className="font-semibold text-sm" style={{ color: model.color }}>{model.name}</span>
                  </div>
                  <div className="text-xs text-gray-400 mb-2">
                    Output: <span className="text-white font-mono bg-gray-600 px-1 rounded">{model.output}</span>
                  </div>
                  <div className="flex flex-wrap gap-1">
                    {model.inputs.map((input, i) => (
                      <span key={i} className="text-xs bg-gray-600 px-2 py-0.5 rounded">{input}</span>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Segmentation */}
          <div className="bg-gray-800 rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 text-center">Segmentación Inteligente</h3>
            <div className="grid grid-cols-4 gap-2">
              {segments.map((seg) => (
                <div key={seg.id} className="bg-gray-700 rounded-lg p-3 text-center" style={{ borderBottom: `3px solid ${seg.color}` }}>
                  <div className="text-2xl mb-1">{seg.icon}</div>
                  <div className="text-lg font-bold" style={{ color: seg.color }}>Seg. {seg.id}</div>
                  <div className="text-xs font-medium my-1">{seg.name}</div>
                  <div className="text-xs text-gray-400 mb-2">{seg.criteria}</div>
                  <div className="text-xs bg-gray-600 rounded px-2 py-1">{seg.action}</div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}

      {activeTab === 'flujo' && (
        <div className="bg-gray-800 rounded-xl p-4">
          <h3 className="text-lg font-semibold mb-4 text-center">⏱️ Flujo Diario de Datos</h3>
          <div className="space-y-2">
            {flowSteps.map((step, index) => (
              <div key={index} className="flex items-center space-x-3 bg-gray-700 rounded-lg p-2">
                <div className="w-16 text-xs font-mono bg-gray-600 rounded px-2 py-1 text-center">
                  {step.time}
                </div>
                <div className="text-xl">{step.icon}</div>
                <div className="flex-1 text-sm font-medium">{step.action}</div>
                <div className={`text-xs px-2 py-1 rounded ${
                  step.owner === 'ML' ? 'bg-purple-600' : 
                  step.owner === 'Bot' ? 'bg-green-600' : 'bg-blue-600'
                }`}>
                  {step.owner}
                </div>
              </div>
            ))}
          </div>
          
          {/* Visual Flow */}
          <div className="mt-6 flex justify-center items-center space-x-2 text-sm">
            <div className="bg-blue-600 px-3 py-2 rounded">Banco</div>
            <div className="text-gray-500">→</div>
            <div className="bg-purple-600 px-3 py-2 rounded">Plataforma ML</div>
            <div className="text-gray-500">→</div>
            <div className="bg-green-600 px-3 py-2 rounded">Voicebot</div>
            <div className="text-gray-500">→</div>
            <div className="bg-purple-600 px-3 py-2 rounded">Feedback</div>
          </div>
        </div>
      )}

      {activeTab === 'impacto' && (
        <div className="space-y-4">
          {/* KPIs */}
          <div className="bg-gray-800 rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-4 text-center">📊 Impacto Esperado</h3>
            <div className="grid grid-cols-5 gap-3">
              {kpis.map((kpi, index) => (
                <div key={index} className="bg-gray-700 rounded-lg p-3 text-center">
                  <div className="text-2xl mb-1">{kpi.icon}</div>
                  <div className="text-xl font-bold text-green-400">{kpi.value}</div>
                  <div className="text-xs font-medium mt-1">{kpi.metric}</div>
                  <div className="text-xs text-gray-400">{kpi.desc}</div>
                </div>
              ))}
            </div>
          </div>

          {/* ROI Summary */}
          <div className="bg-gradient-to-r from-green-900 to-green-800 rounded-xl p-4">
            <h3 className="text-lg font-semibold mb-3 text-center">💰 Resumen de Valor</h3>
            <div className="grid grid-cols-3 gap-4 text-center">
              <div>
                <div className="text-2xl font-bold text-green-300">$65B</div>
                <div className="text-xs text-gray-300">Recupero adicional/año</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-300">$15B</div>
                <div className="text-xs text-gray-300">Ahorro operativo/año</div>
              </div>
              <div>
                <div className="text-2xl font-bold text-green-300">15x</div>
                <div className="text-xs text-gray-300">ROI primer año</div>
              </div>
            </div>
          </div>

          {/* Before/After */}
          <div className="grid grid-cols-2 gap-4">
            <div className="bg-red-900 bg-opacity-30 rounded-xl p-4 border border-red-700">
              <h4 className="font-semibold text-red-400 mb-2">❌ Sin ML (Actual)</h4>
              <ul className="text-xs space-y-1 text-gray-300">
                <li>• CTI plano, llama a todos igual</li>
                <li>• Sin priorización inteligente</li>
                <li>• Mismo flujo para todos</li>
                <li>• Solo reporte básico</li>
              </ul>
            </div>
            <div className="bg-green-900 bg-opacity-30 rounded-xl p-4 border border-green-700">
              <h4 className="font-semibold text-green-400 mb-2">✅ Con ML (Propuesta)</h4>
              <ul className="text-xs space-y-1 text-gray-300">
                <li>• CTI enriquecido con scoring</li>
                <li>• Segmentación A/B/C/D</li>
                <li>• Personalización por cliente</li>
                <li>• Dashboard + feedback loop</li>
              </ul>
            </div>
          </div>
        </div>
      )}

      {/* Footer */}
      <div className="text-center mt-6 text-gray-500 text-xs">
        Arquitectura diseñada para complementar el Piloto Voicebot del Banco de Bogotá
      </div>
    </div>
  );
};

export default ArquitecturaVoicebot;
