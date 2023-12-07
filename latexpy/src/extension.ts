// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { exec } from 'child_process';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "latexpy" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('latexpy.psuedo2Python', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user
		vscode.window.showInformationMessage('Hello World from LatexPy!');

		const pythonScriptPath = 'C:/Users/szens/OneDrive/Desktop/DesktopShit/CompSci/LatexPy-Extension/latexpy/src/pseudo2Python.py';
        const editor = vscode.window.activeTextEditor

        if (editor) {
            const document = editor.document;
            const selection = editor.selection;

            // If text is selected, use the selection; otherwise, use the entire document content
            const latexInput = selection.isEmpty ? document.getText() : document.getText(selection);

            const command = `python ${pythonScriptPath} "${latexInput}"`; // r"""?

            exec(command, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error: ${error.message}`);
                    return;
                }

                console.log(`Output: ${stdout}`);
            });
		}
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
