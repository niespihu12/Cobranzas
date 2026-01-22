# Instalación Auto-Refresh

## Instalar la librería

```bash
pip install streamlit-autorefresh
```

## Cómo funciona

1. **Activar auto-actualización**: En el sidebar, marca el checkbox "Auto-actualizar cada 1 minuto"

2. **Funcionamiento automático**: El dashboard se recargará automáticamente cada 60 segundos y traerá los datos más recientes de Google Sheets

3. **Sin interacción necesaria**: No necesitas hacer clic ni cambiar de tab, la actualización es completamente automática

## Verificar instalación

```bash
pip show streamlit-autorefresh
```

## Uso

- Marca el checkbox "Auto-actualizar cada 1 minuto" en el sidebar
- El contador mostrará el número de actualizaciones realizadas
- Los datos se recargarán automáticamente desde Google Sheets cada minuto
- La hora de última actualización se muestra en el panel de información

## Nota

Si no instalas la librería, el dashboard seguirá funcionando normalmente pero sin auto-actualización automática.
