const nodemailer = require('nodemailer');

module.exports = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { name, email, privacy, cv } = req.body;

    if (!name || !email || !privacy || !cv || !cv.filename || !cv.content) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    // Header-Injection verhindern: Zeilenumbrueche aus dem Namen entfernen
    const safeName = String(name).replace(/[\r\n]+/g, ' ').trim().slice(0, 100);

    const allowedExtensions = ['.pdf', '.doc', '.docx'];
    const ext = cv.filename.slice(cv.filename.lastIndexOf('.')).toLowerCase();
    if (!allowedExtensions.includes(ext)) {
        return res.status(400).json({ error: 'Invalid file type' });
    }

    const MAX_CV_SIZE = 2 * 1024 * 1024;
    const cvSize = (cv.content.length * 3) / 4;
    if (cvSize > MAX_CV_SIZE * 1.1) {
        return res.status(400).json({ error: 'CV file too large' });
    }

    try {
        const transporter = nodemailer.createTransport({
            host: 'smtp.ionos.de',
            port: 465,
            secure: true,
            auth: {
                user: process.env.SMTP_USER,
                pass: process.env.SMTP_PASS,
            },
        });

        const mailOptions = {
            from: '"NextGen Webseite" <info@nextgenforum.de>',
            to: 'info@nextgenforum.de',
            replyTo: email,
            subject: `[CV-Check] ${safeName} hat einen CV hochgeladen`,
            text: `Neue CV-Check-Anfrage eingegangen.

Leistung: CV-Check
Name: ${safeName}
E-Mail: ${email}
Datei: ${cv.filename}
Datenschutz akzeptiert: ${privacy ? 'JA' : 'NEIN'}
            `,
            html: `
        <h3>Neue Anfrage: CV-Check</h3>
        <p><strong>Name:</strong> ${safeName}</p>
        <p><strong>E-Mail:</strong> ${email}</p>
        <p><strong>Datei:</strong> ${cv.filename}</p>
        <p><strong>Datenschutz akzeptiert:</strong> ${privacy ? '✅ Ja' : '❌ Nein'}</p>
      `,
            attachments: [
                {
                    filename: cv.filename,
                    content: cv.content,
                    encoding: 'base64'
                }
            ]
        };

        await transporter.sendMail(mailOptions);

        return res.status(200).json({ message: 'CV check request sent successfully' });
    } catch (error) {
        console.error('Error sending CV check email:', error);
        return res.status(500).json({ error: 'Failed to send request. Please try again later.' });
    }
};
