#!/usr/bin/env node

const { spawn } = require('child_process');
const readline = require('readline');

const commands = {
  '1': { name: 'Development Server', cmd: 'npm', args: ['run', 'dev'] },
  '2': { name: 'Run Tests', cmd: 'npm', args: ['test'] },
  '3': { name: 'Run Tests with Coverage', cmd: 'npm', args: ['run', 'test:coverage'] },
  '4': { name: 'Check Code Quality', cmd: 'npm', args: ['run', 'quality'] },
  '5': { name: 'Fix Code Quality Issues', cmd: 'npm', args: ['run', 'quality:fix'] },
  '6': { name: 'Full Quality Check', cmd: 'npm', args: ['run', 'quality:full'] },
  '7': { name: 'Format All Code', cmd: 'npm', args: ['run', 'all:format'] },
  '8': { name: 'Check Dependencies', cmd: 'npm', args: ['run', 'check-deps'] },
  '9': { name: 'Check for Updates', cmd: 'npm', args: ['run', 'check-updates'] },
  '10': { name: 'Build for Production', cmd: 'npm', args: ['run', 'build'] },
  '11': { name: 'Analyze Bundle Size', cmd: 'npm', args: ['run', 'analyze'] },
  '12': { name: 'Find Dead Code', cmd: 'npm', args: ['run', 'find-deadcode'] },
  '13': { name: 'Python Quality Check', cmd: 'npm', args: ['run', 'python:quality'] },
  '14': { name: 'Full Stack Quality Check', cmd: 'npm', args: ['run', 'all:quality'] },
  '15': { name: 'Clean Build Artifacts', cmd: 'npm', args: ['run', 'clean'] },
  'q': { name: 'Quit', cmd: null },
};

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function clearScreen() {
  process.stdout.write('\x1Bc');
}

function showMenu() {
  clearScreen();
  console.log('\n🧠 FreeAgentics Development CLI\n');
  console.log('📋 Available Commands:\n');

  Object.entries(commands).forEach(([key, { name }]) => {
    if (key === 'q') {
      console.log(`\n  ${key}) ${name}`);
    } else {
      console.log(`  ${key.padStart(2)}) ${name}`);
    }
  });

  console.log('\n');
}

function runCommand(cmd, args) {
  return new Promise((resolve) => {
    const child = spawn(cmd, args, { stdio: 'inherit', shell: true });

    child.on('close', (code) => {
      if (code !== 0) {
        console.log(`\n❌ Command exited with code ${code}`);
      }
      resolve();
    });

    child.on('error', (err) => {
      console.error(`\n❌ Failed to start command: ${err.message}`);
      resolve();
    });
  });
}

async function promptUser() {
  showMenu();

  rl.question('Enter command number (or q to quit): ', async (answer) => {
    const choice = answer.toLowerCase().trim();

    if (choice === 'q') {
      console.log('\n👋 Goodbye!\n');
      rl.close();
      process.exit(0);
    }

    const command = commands[choice];

    if (!command) {
      console.log('\n❌ Invalid choice. Please try again.');
      setTimeout(promptUser, 2000);
      return;
    }

    console.log(`\n🚀 Running: ${command.name}\n`);

    await runCommand(command.cmd, command.args);

    console.log('\n✅ Command completed. Press Enter to continue...');

    rl.question('', () => {
      promptUser();
    });
  });
}

// Handle Ctrl+C gracefully
process.on('SIGINT', () => {
  console.log('\n\n👋 Goodbye!\n');
  process.exit(0);
});

// Start the CLI
console.log('🧠 Welcome to FreeAgentics Development CLI');
promptUser();
