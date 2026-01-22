import React, { useState } from 'react';

const ArquitecturaVoicebot = () => {
  const [activeLayer, setActiveLayer] = useState(null);
  
  const layers = [
    {
      id: 'data',
      name: 'Capa de Datos',
      color: '#3B82F6',
      components: ['Core Bancario', 'Archivo CTI', 'Centrales Riesgo', 'Data Lake'],
      description: 'Fuentes de datos y almacenamiento centralizado'
    },
    {
      id: 'ml',
      name: 'Capa de Inteligencia (ML)',
      color: '#8B5CF6',
      components: ['Feature Engineering', 'Modelo Prob. Pago', 'Modelo Contactabilidad', 'Modelo Mejor Hora', 'Modelo Receptividad', 'Segmentación'],
      description: 'Modelos XGBoost para scoring y predicción'
    },
    {
      id: 'decision',
      name: 'Motor de Decisión',
      color: '#EC4899',
      components: ['Reglas de Negocio', 'Orquestador', 'CTI Enriquecido', 'Personalización'],
      description: 'Combina ML + reglas para decisiones finales'
    },
    {
      id: 'execution',
      name: 'Capa de Ejecución',
      color: '#10B981',
      components: ['Voicebot (Piloto)', 'Seguimiento IA', 'Call Center', 'Captura Resultados'],
      description: 'Canales de contacto y captura de resultados'
    },
    {
      id: 'observability',
      name: 'Observabilidad',
      color: '#F59E0B',
      components: ['Dashboard Operativo', 'Dashboard Analítico', 'Validación ML', 'Feedback Loop'],
      description: 'Monitoreo, métricas y mejora continua'
    }
  ];

  const flowSteps = [
    { time: '05:00', action: 'Extracción CTI', owner: 'Banco de Bogotá' },
    { time: '06:00', action: 'Feature Engineering', owner: 'Plataforma ML' },
    { time: '06:30', action: 'Scoring XGBoost', owner: 'Plataforma ML' },
    { time: '07:00', action: 'Motor de Decisión', owner: 'Plataforma ML' },
    { time: '07:30', action: 'CTI Enriquecido', owner: 'Plataforma ML' },
    { time: '08:00-20:00', action: 'Ejecución Voicebot', owner: 'Proveedor' },
    { time: '21:00', action: 'Resultados', owner: 'Proveedor' },
    { time: '22:00', action: 'Feedback Loop', owner: 'Plataforma ML' }
  ];

  const techStack = [
    { category: 'Infraestructura', techs: ['Azure AKS', 'Azure Data Lake', 'Azure ML'] },
    { category: 'Data', techs: ['Apache Spark', 'PostgreSQL', 'Redis', 'Delta Lake'] },
    { category: 'ML/AI', techs: ['XGBoost', 'Scikit-learn', 'MLflow', 'SHAP'] },
    { category: 'Backend', techs: ['Python', 'FastAPI', 'Celery', 'RabbitMQ'] },
    { category: 'Observabilidad', techs: ['Prometheus', 'Grafana', 'ELK Stack'] }
  ];

  return (
    <div className="min-h-screen bg-gray-900 text-white p-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold mb-2">Arquitectura de Producto</h1>
        <h2 className="text-xl text-blue-400">Capa de Inteligencia para Voicebot de Cobranzas</h2>
        <p className="text-gray-400 mt-2">Banco de Bogotá</p>
      </div>

      {/* Main Architecture Diagram */}
      <div className="bg-gray-800 rounded-xl p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4 text-center">Arquitectura por Capas</h3>
        
        <div className="space-y-3">
          {layers.map((layer, index) => (
            <div
              key={layer.id}
              className={`rounded-lg p-4 cursor-pointer transition-all duration-300 ${
                activeLayer === layer.id ? 'ring-2 ring-white scale-102' : 'hover:opacity-90'
              }`}
              style={{ backgroundColor: layer.color + '20', borderLeft: `4px solid ${layer.color}` }}
              onClick={() => setActiveLayer(activeLayer === layer.id ? null : layer.id)}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="font-semibold" style={{ color: layer.color }}>{layer.name}</span>
                  <p className="text-sm text-gray-400 mt-1">{layer.description}</p>
                </div>
                <div className="text-2xl">{activeLayer === layer.id ? '▼' : '▶'}</div>
              </div>
              
              {activeLayer === layer.id && (
                <div className="mt-4 grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-2">
                  {layer.components.map((comp, i) => (
                    <div
                      key={i}
                      className="bg-gray-700 rounded px-3 py-2 text-sm text-center"
                    >
                      {comp}
                    </div>
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        {/* Flow arrows */}
        <div className="flex justify-center my-4">
          <div className="flex items-center space-x-2 text-gray-500">
            <span>↓</span>
            <span className="text-sm">Flujo de datos</span>
            <span>↓</span>
          </div>
        </div>
      </div>

      {/* Two Column Layout */}
      <div className="grid md:grid-cols-2 gap-6 mb-8">
        {/* Daily Flow */}
        <div className="bg-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <span className="mr-2">⏱️</span>
            Flujo Diario de Datos
          </h3>
          <div className="space-y-2">
            {flowSteps.map((step, index) => (
              <div key={index} className="flex items-center space-x-3">
                <div className="w-24 text-xs font-mono bg-gray-700 rounded px-2 py-1 text-center">
                  {step.time}
                </div>
                <div className="flex-1 bg-gray-700 rounded px-3 py-2 text-sm">
                  {step.action}
                </div>
                <div className="text-xs text-gray-400 w-24 text-right">
                  {step.owner}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Tech Stack */}
        <div className="bg-gray-800 rounded-xl p-6">
          <h3 className="text-lg font-semibold mb-4 flex items-center">
            <span className="mr-2">🛠️</span>
            Stack Tecnológico
          </h3>
          <div className="space-y-4">
            {techStack.map((cat, index) => (
              <div key={index}>
                <div className="text-sm font-medium text-gray-400 mb-2">{cat.category}</div>
                <div className="flex flex-wrap gap-2">
                  {cat.techs.map((tech, i) => (
                    <span
                      key={i}
                      className="bg-blue-600 bg-opacity-30 text-blue-300 px-3 py-1 rounded-full text-sm"
                    >
                      {tech}
                    </span>
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Integration Architecture */}
      <div className="bg-gray-800 rounded-xl p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4 text-center">Arquitectura de Integración</h3>
        
        <div className="flex flex-col items-center space-y-4">
          {/* Banco de Bogotá */}
          <div className="w-full max-w-4xl bg-blue-900 bg-opacity-30 rounded-lg p-4 border border-blue-700">
            <div className="text-center font-semibold text-blue-400 mb-3">BANCO DE BOGOTÁ</div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-blue-300">Core Bancario</div>
                <div className="text-xs text-gray-400 mt-1">Saldos, Productos, Pagos</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-blue-300">AdminFO</div>
                <div className="text-xs text-gray-400 mt-1">Gestión de Cartera</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-blue-300">Centrales Riesgo</div>
                <div className="text-xs text-gray-400 mt-1">DataCrédito, TransUnion</div>
              </div>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex flex-col items-center">
            <div className="text-gray-500">SFTP / API</div>
            <div className="text-2xl">↓</div>
          </div>

          {/* Plataforma ML */}
          <div className="w-full max-w-4xl bg-purple-900 bg-opacity-30 rounded-lg p-4 border border-purple-700">
            <div className="text-center font-semibold text-purple-400 mb-3">PLATAFORMA DE INTELIGENCIA</div>
            <div className="grid grid-cols-4 gap-3">
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-purple-300">API Gateway</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-purple-300">Servicio Ingesta</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-purple-300">Servicio Scoring</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-purple-300">Servicio Reportes</div>
              </div>
            </div>
            <div className="mt-3 bg-gray-700 rounded p-2 text-center text-sm">
              <span className="text-purple-300">Message Queue</span>
              <span className="text-gray-400 text-xs ml-2">(RabbitMQ / Kafka)</span>
            </div>
          </div>

          {/* Arrow */}
          <div className="flex flex-col items-center">
            <div className="text-gray-500">SFTP / API</div>
            <div className="text-2xl">↓</div>
          </div>

          {/* Voicebot */}
          <div className="w-full max-w-4xl bg-green-900 bg-opacity-30 rounded-lg p-4 border border-green-700">
            <div className="text-center font-semibold text-green-400 mb-3">PROVEEDOR VOICEBOT (Piloto)</div>
            <div className="grid grid-cols-3 gap-4">
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-green-300">Recibe CTI</div>
                <div className="text-xs text-gray-400 mt-1">Enriquecido con ML</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-green-300">Ejecuta Llamadas</div>
                <div className="text-xs text-gray-400 mt-1">Flujo conversacional</div>
              </div>
              <div className="bg-gray-700 rounded p-3 text-center text-sm">
                <div className="text-green-300">Envía Resultados</div>
                <div className="text-xs text-gray-400 mt-1">CSV / Excel</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Models Detail */}
      <div className="bg-gray-800 rounded-xl p-6 mb-8">
        <h3 className="text-lg font-semibold mb-4 text-center">Modelos XGBoost</h3>
        
        <div className="grid md:grid-cols-4 gap-4">
          {[
            { name: 'Probabilidad de Pago', output: 'prob [0-1]', inputs: ['Hist. pagos', 'Días mora', 'Capacidad pago'], color: '#3B82F6' },
            { name: 'Contactabilidad', output: 'prob [0-1]', inputs: ['Teléfonos', 'Intentos prev.', 'Horarios resp.'], color: '#8B5CF6' },
            { name: 'Mejor Hora', output: 'hora [0-3]', inputs: ['Patrones', 'Ocupación', 'Historial'], color: '#EC4899' },
            { name: 'Receptividad Bot', output: 'prob [0-1]', inputs: ['Edad', 'Digital', 'Hist. bot'], color: '#10B981' }
          ].map((model, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4" style={{ borderTop: `3px solid ${model.color}` }}>
              <div className="font-semibold text-sm mb-2" style={{ color: model.color }}>{model.name}</div>
              <div className="text-xs text-gray-400 mb-3">
                Output: <span className="text-white font-mono">{model.output}</span>
              </div>
              <div className="text-xs text-gray-400">Inputs:</div>
              <ul className="text-xs mt-1 space-y-1">
                {model.inputs.map((input, i) => (
                  <li key={i} className="text-gray-300">• {input}</li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        {/* Segmentation output */}
        <div className="mt-6 grid grid-cols-4 gap-3">
          {[
            { segment: 'A', name: 'Voicebot Prioritario', criteria: 'prob_pago ≥ 0.5, recept ≥ 0.6', color: '#10B981' },
            { segment: 'B', name: 'Voicebot + Seguimiento', criteria: 'prob_pago ≥ 0.3, recept ≥ 0.4', color: '#3B82F6' },
            { segment: 'C', name: 'Derivar a Humano', criteria: 'recept < 0.4 o monto > $10M', color: '#F59E0B' },
            { segment: 'D', name: 'No Gestionar Hoy', criteria: 'prob_pago < 0.1, contacto < 0.2', color: '#EF4444' }
          ].map((seg, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-3 text-center" style={{ borderBottom: `3px solid ${seg.color}` }}>
              <div className="text-2xl font-bold mb-1" style={{ color: seg.color }}>Seg. {seg.segment}</div>
              <div className="text-sm font-medium mb-1">{seg.name}</div>
              <div className="text-xs text-gray-400">{seg.criteria}</div>
            </div>
          ))}
        </div>
      </div>

      {/* KPIs */}
      <div className="bg-gray-800 rounded-xl p-6">
        <h3 className="text-lg font-semibold mb-4 text-center">Impacto Esperado</h3>
        
        <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
          {[
            { metric: 'Contactabilidad', value: '+25%', desc: 'Llamar en mejor hora' },
            { metric: 'Tasa Aceptación', value: '+30%', desc: 'Orden óptimo mecanismos' },
            { metric: 'Costo/Gestión', value: '-35%', desc: 'No llamar segmento D' },
            { metric: 'Cumplimiento', value: '100%', desc: 'Ley 2300' },
            { metric: 'Eficiencia', value: '+20%', desc: 'Priorizar cabeza mora' }
          ].map((kpi, index) => (
            <div key={index} className="bg-gray-700 rounded-lg p-4 text-center">
              <div className="text-2xl font-bold text-green-400">{kpi.value}</div>
              <div className="text-sm font-medium mt-1">{kpi.metric}</div>
              <div className="text-xs text-gray-400 mt-1">{kpi.desc}</div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="text-center mt-8 text-gray-500 text-sm">
        Arquitectura diseñada para complementar el Piloto Voicebot del Banco de Bogotá
      </div>
    </div>
  );
};

export default ArquitecturaVoicebot;
