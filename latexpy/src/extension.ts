// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
import * as vscode from 'vscode';
import { exec } from 'child_process';
import * as fs from 'fs';

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
export function activate(context: vscode.ExtensionContext) {

	// Use the console to output diagnostic information (console.log) and errors (console.error)
	// This line of code will only be executed once when your extension is activated
	console.log('Congratulations, your extension "latexpy" is now active!');

	// The command has been defined in the package.json file
	// Now provide the implementation of the command with registerCommand
	// The commandId parameter must match the command field in package.json
	let disposable = vscode.commands.registerCommand('latexpy.pseudo2Python', () => {
		// The code you place here will be executed every time your command is executed
		// Display a message box to the user

		const pythonScriptPath = 'C:/Users/amara/OneDrive/Desktop/DesktopShit/CompSci/LatexPy-Extension/latexpy/src/pseudo2Python.py';
        const editor = vscode.window.activeTextEditor

        if (editor) {
            const document = editor.document;
            const selection = editor.selection;

            // If text is selected, use the selection; otherwise, use the entire document content
            const latexInput = selection.isEmpty ? document.getText() : document.getText(selection);
            const filePath = 'C:/Users/amara/OneDrive/Desktop/DesktopShit/CompSci/LatexPy-Extension/latexpy/src/test.txt';
            fs.writeFileSync(filePath, latexInput);
            const command = `python ${pythonScriptPath} "${filePath}"`; // r"""?
            // const command = `python -c "from PseudocodePy import p; p(r"""${latexInput}""")"`;

            exec(command, (error, stdout, stderr) => {
                if (error) {
                    console.error(`Error: ${error.message}`);
                    return;
                }
                const python_out = stdout;

                const regex = /latexpy_result([\s\S]*)/;

                // Use the regular expression to extract the matching part
                const match = python_out.match(regex);

                // Check if there's a match
                if (match && match[1]) {
                    const result = match[1].trim();
                    console.log(result);
                    editor.edit((editBuilder) => {
                        editBuilder.replace(selection, "\n\n" + result)
                    })
                    vscode.window.showInformationMessage('Latex Parsed Successfully');
                } else {
                    console.log('Match not found');
                }
            });
		}
	});

	context.subscriptions.push(disposable);
}

// This method is called when your extension is deactivated
export function deactivate() {}
