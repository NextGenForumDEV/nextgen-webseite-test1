const nodemailer = require('nodemailer');

module.exports = async (req, res) => {
    if (req.method !== 'POST') {
        return res.status(405).json({ error: 'Method not allowed' });
    }

    const {
        program,
        firstname,
        lastname,
        email,
        cv,
        transcript,
        agreements
    } = req.body;

    // Basic Validation
    if (!program || !firstname || !lastname || !email || !cv || !transcript || !agreements) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    // Size Validation (Double Check Backend Side)
    // Base64 string length = 4 * (size / 3). Approx check.
    const MAX_CV_SIZE = 1 * 1024 * 1024;
    const MAX_TRANSCRIPT_SIZE = 3 * 1024 * 1024;

    // Very rough base64 to byte size estimation: (len * 3) / 4
    const cvSize = (cv.content.length * 3) / 4;
    const transcriptSize = (transcript.content.length * 3) / 4;

    if (cvSize > MAX_CV_SIZE * 1.1) { // 10% buffer for base64 calculation inaccuracies
        return res.status(400).json({ error: 'CV file too large' });
    }
    if (transcriptSize > MAX_TRANSCRIPT_SIZE * 1.1) {
        return res.status(400).json({ error: 'Transcript file too large' });
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
            subject: `Bewerbung: ${program.substring(0, 30)}... - ${firstname} ${lastname}`,
            text: `Neue Bewerbung eingegangen.
            
Programm: ${program}
Vorname: ${firstname}
Nachname: ${lastname}
E-Mail: ${email}

Zustimmungen:
- Commitment Pflichtteilnahme: ${agreements.commitment ? 'JA' : 'NEIN'}
- Datenschutz: ${agreements.privacy ? 'JA' : 'NEIN'}
- Foto/Video: ${agreements.media ? 'JA' : 'NEIN'}
            `,
            html: `
        <h3>Neue Bewerbung eingegangen</h3>
        <p><strong>Programm:</strong> ${program}</p>
        <p><strong>Bewerber:</strong> ${firstname} ${lastname}</p>
        <p><strong>E-Mail:</strong> ${email}</p>
        <br>
        <h4>Zustimmungen:</h4>
        <ul>
            <li><strong>Commitment Pflichtteilnahme:</strong> ${agreements.commitment ? '✅ Akzeptiert' : '❌ Nicht akzeptiert'}</li>
            <li><strong>Datenschutz:</strong> ${agreements.privacy ? '✅ Akzeptiert' : '❌ Nicht akzeptiert'}</li>
             <li><strong>Foto/Video Nutzung:</strong> ${agreements.media ? '✅ Akzeptiert' : '❌ Nicht akzeptiert'}</li>
        </ul>
      `,
            attachments: [
                {
                    filename: cv.filename,
                    content: cv.content,
                    encoding: 'base64'
                },
                {
                    filename: transcript.filename,
                    content: transcript.content,
                    encoding: 'base64'
                }
            ]
        };

        await transporter.sendMail(mailOptions);

        return res.status(200).json({ message: 'Application sent successfully' });
    } catch (error) {
        console.error('Error sending application email:', error);
        return res.status(500).json({ error: 'Failed to send application. Please try again later.' });
    }
};
