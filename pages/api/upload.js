// pages/api/upload.js
import cloudinary from '@/lib/cloudinary';

export const config = {
  api: {
    bodyParser: {
      sizeLimit: '100mb',
    },
  },
};

export default async function handler(req, res) {
  if (req.method === 'POST') {
    const { file } = req.body;

    try {
      const result = await cloudinary.uploader.upload(file, {
        resource_type: 'auto',
        folder: 'lovanote',
      });

      return res.status(200).json({ url: result.secure_url });
    } catch (error) {
      return res.status(500).json({ error: 'Cloudinary upload failed', details: error.message });
    }
  }

  res.status(405).json({ error: 'Method Not Allowed' });
}
