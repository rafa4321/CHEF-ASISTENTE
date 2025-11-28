// api/chat.js
// Este archivo se ejecuta de forma segura en el servidor de Vercel.
// La clave API es leída desde las Variables de Entorno de Vercel (PASO 3).

export default async function handler(req, res) {
  // Aquí tomamos la clave segura del servidor (Vercel)
  const apiKey = process.env.GEMINI_API_KEY; 

  if (!apiKey) {
    return res.status(500).json({ error: "Clave API no configurada en el servidor. Debe configurar GEMINI_API_KEY en Vercel." });
  }

  const { message } = req.body;

  try {
    // Conexión segura a Google (oculta al navegador)
    const response = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contents: [{ parts: [{ text: message }] }],
        config: {
             systemInstruction: { parts: [{ text: "Eres un chef experto llamado Sabor Expres. Responde solo sobre cocina, recetas y alimentos. Sé amable y usa emojis y habla siempre en español." }] }
        }
      })
    });

    const data = await response.json();
    
    // Manejar errores de la API de Google
    if (data.error) {
        throw new Error(data.error.message);
    }
    
    // Enviamos la respuesta limpia al HTML
    const text = data.candidates[0].content.parts[0].text;
    res.status(200).json({ reply: text });
    
  } catch (error) {
    console.error("Error en la conexión con Gemini:", error);
    res.status(500).json({ error: "Error interno del Chef. La clave API puede ser inválida o el servicio está inactivo." });
  }
}
