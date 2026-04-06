import os
from dotenv import load_dotenv
from google import genai
import gradio as gr

# Cargar variables
load_dotenv()

# Cliente Gemini
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generar_plan(nivel, molestias):
    if not nivel:
        return "Debes seleccionar un nivel."

    if not molestias:
        molestias = "ninguna"

    prompt = f"""
    Actúa como un entrenador profesional de CrossFit.

    Usuario:
    - Nivel: {nivel}
    - Molestias: {molestias}

    Genera un plan de entrenamiento de 5 días.

    Formato obligatorio:

    Día 1:
    - Calentamiento:
    - Parte principal:
    - WOD:

    Día 2:
    ...

    Reglas:
    - Ajusta intensidad según nivel
    - Si hay molestias, adapta ejercicios
    - Usa lenguaje claro
    - No expliques teoría, solo el plan
    """

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt
    )

    return response.text

# Interfaz Gradio
interfaz = gr.Interface(
    fn=generar_plan,
    inputs=[
        gr.Dropdown(
            choices=["principiante", "intermedio", "avanzado"],
            label="Nivel de CrossFit"
        ),
        gr.Textbox(label="Molestias o lesiones", placeholder="Ej: dolor de rodilla, hombro, etc.")
    ],
    outputs=gr.Textbox(label="Plan de entrenamiento"),
    title="Agente de Entrenamiento CrossFit",
    description="Genera un plan personalizado de 5 días basado en tu nivel y molestias"
)

if __name__ == "__main__":
    interfaz.launch()