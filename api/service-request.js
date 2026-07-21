const nodemailer = require('nodemailer');

const SERVICES = {
    probono: {
        label: 'Pro-Bono-Beratung',
        subjectFor: (name) => `[Pro-Bono-Beratung] ${name} hat eine Beratung angefragt`
    },
    support: {
        label: 'Karriere-Support',
        subjectFor: (name) => `[Karriere-Support] ${name} hat Karriere-Support angefragt`
    },
    thesis: {
        label: 'Förderung Abschlussarbeit',
        subjectFor: (name) => `[Abschlussarbeit] ${name} hat eine Förderung für eine Abschlussarbeit angefragt`
    }
};

module.exports = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const { service, name, email, message, privacy } = req.body;

    if (!service || !name || !email || !message || !privacy) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    const svc = SERVICES[service];
    if (!svc) {
        return res.status(400).json({ error: 'Unknown service' });
    }

    // Header-Injection verhindern: Zeilenumbrueche aus dem Namen entfernen
    const safeName = String(name).replace(/[\r\n]+/g, ' ').trim().slice(0, 100);

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
            subject: svc.subjectFor(safeName),
            text: `Neue Anfrage über die Website eingegangen.

Leistung: ${svc.label}
Name: ${safeName}
E-Mail: ${email}
Datenschutz akzeptiert: ${privacy ? 'JA' : 'NEIN'}

Anliegen:
${message}
            `,
            html: `
        <h3>Neue Anfrage: ${svc.label}</h3>
        <p><strong>Name:</strong> ${safeName}</p>
        <p><strong>E-Mail:</strong> ${email}</p>
        <p><strong>Datenschutz akzeptiert:</strong> ${privacy ? '✅ Ja' : '❌ Nein'}</p>
        <h4>Anliegen:</h4>
        <p>${String(message).replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;').replace(/\n/g, '<br>')}</p>
      `
        };

        await transporter.sendMail(mailOptions);

        return res.status(200).json({ message: 'Request sent successfully' });
    } catch (error) {
        console.error('Error sending service request email:', error);
        return res.status(500).json({ error: 'Failed to send request. Please try again later.' });
    }
};
