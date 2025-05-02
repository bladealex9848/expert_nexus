# Documento Avanzado de Prueba

## Características Avanzadas de Markdown

Este documento contiene características más avanzadas para probar la robustez de la conversión a PDF.

### Notas al pie

Aquí hay una nota al pie[^1].

[^1]: Esta es la nota al pie.

### Definiciones

Término
: Definición del término
: Otra definición del mismo término

### Tablas complejas

| Función | Descripción | Ejemplo | Resultado |
|---------|-------------|---------|-----------|
| `sum()` | Suma los elementos de una lista | `sum([1, 2, 3])` | `6` |
| `len()` | Devuelve la longitud de un objeto | `len("hello")` | `5` |
| `map()` | Aplica una función a cada elemento | `map(lambda x: x*2, [1, 2, 3])` | `[2, 4, 6]` |

### Bloques de código con resaltado de sintaxis

```python
import numpy as np
import matplotlib.pyplot as plt

# Generar datos
x = np.linspace(0, 10, 100)
y = np.sin(x)

# Crear gráfico
plt.figure(figsize=(10, 6))
plt.plot(x, y, 'b-', linewidth=2, label='sin(x)')
plt.title('Gráfico de la función seno')
plt.xlabel('x')
plt.ylabel('sin(x)')
plt.grid(True)
plt.legend()
plt.show()
```

### HTML embebido

<div style="background-color: #f0f0f0; padding: 10px; border-radius: 5px;">
  <h3>Este es un bloque HTML</h3>
  <p>Con <strong>formato</strong> y <em>estilos</em> personalizados.</p>
  <ul>
    <li>Elemento 1</li>
    <li>Elemento 2</li>
  </ul>
</div>

### Diagrama ASCII complejo

```
                    +-------------+
                    |             |
                    |   Cliente   |
                    |             |
                    +------+------+
                           |
                           | HTTP/HTTPS
                           v
+------------+      +------+------+      +-------------+
|            |      |             |      |             |
| Base de    +<---->+   Servidor  +<---->+  Servicios  |
| Datos      |      |             |      |  Externos   |
|            |      +------+------+      +-------------+
+------------+             |
                           | WebSocket
                           v
                    +------+------+
                    |             |
                    | Notificación|
                    |             |
                    +-------------+
```

### Listas de tareas

- [x] Tarea completada
- [ ] Tarea pendiente
- [ ] Otra tarea pendiente
  - [x] Subtarea completada
  - [ ] Subtarea pendiente

### Emojis

:smile: :heart: :thumbsup: :rocket: :computer:

### Texto con colores (usando HTML)

<span style="color: red;">Texto en rojo</span>, <span style="color: blue;">texto en azul</span>, <span style="color: green;">texto en verde</span>.

### Superíndices y subíndices

H<sub>2</sub>O y E = mc<sup>2</sup>

## Conclusión

Este documento avanzado prueba características más complejas de Markdown para asegurar que la conversión a PDF sea robusta y fiel al formato original.
