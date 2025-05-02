import { spawn } from 'child_process';
import { NextResponse } from 'next/server';
import fs from 'fs/promises';
import path from 'path';

export async function POST(req) {
  try {
    console.log('📥 Incoming POST request to /api/transcribe');

    // Parse multipart form data
    const formData = await req.formData();
    const file = formData.get('audio'); // Ensure this matches the frontend key

    if (!file) {
      console.error('❌ No file found in form data');
      return NextResponse.json({ error: 'No file provided' }, { status: 400 });
    }

    // Convert file to buffer
    const bytes = await file.arrayBuffer();
    const buffer = Buffer.from(bytes);

    // Save to temporary directory
    const tempDir = '/tmp';
    const filePath = path.join(tempDir, file.name);
    await fs.writeFile(filePath, buffer);
    console.log(`📁 Saved file to ${filePath}`);

    // Spawn the Python Whisper process
    const python = spawn('python3', ['whisper-transcribe.py', filePath]);

    // Prepare to stream data back to client
    const readableStreamDefaultWriter = new ReadableStream({
      start(controller) {
        let output = '';
        let errorOutput = '';

        // Listen for data from the Python process
        python.stdout.on('data', (data) => {
          output += data.toString();
          
          // Send progress update to the client
          if (output.includes('Progress:')) {
            const progressMatch = output.match(/Progress:\s*(\d+)%/);
            if (progressMatch) {
              const progress = progressMatch[1];
              controller.enqueue(`Progress: ${progress}%\n`);
            }
          }
        });

        // Listen for error output from the Python process
        python.stderr.on('data', (data) => {
          errorOutput += data.toString();
        });

        // Handle process close and send final result
        python.on('close', (code) => {
          if (code === 0) {
            controller.enqueue(`Transcription: ${output.trim()}`);
          } else {
            console.error('❌ Python error:', errorOutput);
            controller.enqueue(`Error: ${errorOutput}`);
          }
          controller.close();
        });
      },
    });

    // Return the streaming response to the client
    return new NextResponse(readableStreamDefaultWriter, {
      status: 200,
      headers: {
        'Content-Type': 'text/plain',
      },
    });

  } catch (err) {
    console.error('❌ Unexpected server error:', err);
    return NextResponse.json({ error: 'Internal server error' }, { status: 500 });
  }
}
