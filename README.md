# AI SDK Python Streaming Preview

This template demonstrates the usage of [Data Stream Protocol](https://sdk.vercel.ai/docs/ai-sdk-ui/stream-protocol#data-stream-protocol) to stream chat completions from a Python endpoint ([FastAPI](https://fastapi.tiangolo.com)) and display them using the [useChat](https://sdk.vercel.ai/docs/ai-sdk-ui/chatbot#chatbot) hook in your Next.js application.

## Deploy your own

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel-labs%2Fai-sdk-preview-python-streaming&env=OPENAI_API_KEY&envDescription=API%20keys%20needed%20for%20application&envLink=https%3A%2F%2Fgithub.com%2Fvercel-labs%2Fai-sdk-preview-python-streaming%2Fblob%2Fmain%2F.env.example)

## How to use

Run [`create-next-app`](https://github.com/vercel/next.js/tree/canary/packages/create-next-app) with [npm](https://docs.npmjs.com/cli/init), [Yarn](https://yarnpkg.com/lang/en/docs/cli/create/), or [pnpm](https://pnpm.io) to bootstrap the example:

```bash
npx create-next-app --example https://github.com/vercel-labs/ai-sdk-preview-python-streaming ai-sdk-preview-python-streaming-example
```

```bash
yarn create next-app --example https://github.com/vercel-labs/ai-sdk-preview-python-streaming ai-sdk-preview-python-streaming-example
```

```bash
pnpm create next-app --example https://github.com/vercel-labs/ai-sdk-preview-python-streaming ai-sdk-preview-python-streaming-example
```

To run the example locally you need to:

1. Sign up for accounts with the AI providers you want to use (e.g., OpenAI, Anthropic).
2. Obtain API keys for each provider.
3. Set the required environment variables as shown in the `.env.example` file, but in a new file called `.env`.
4. `pnpm install` to install the required Node dependencies.
5. `virtualenv venv` to create a virtual environment.
6. `source venv/bin/activate` to activate the virtual environment.
7. `pip install -r requirements.txt` to install the required Python dependencies.
8. `pnpm dev` to launch the development server.

## Firestore Emulator & Pytest

The backend integration tests expect a running Firestore instance. For local development you can rely on the Firebase Emulator:

1. Ensure Python deps are installed (`make init` and optionally `make install-dev`).
2. Start the emulator in a separate terminal with `npm run firebase:emulator` or `make firebase-emulator`. The command uses `npx firebase-tools` so no global install is required.
3. In another terminal run the tests against the emulator with `make test-firestore` or `npm run test:firestore`. Both commands automatically set the required `FIRESTORE_EMULATOR_HOST` and prefer the local `.venv` Python if it exists (falling back to `python3`).

When the emulator is not running the Firestore integration tests will be skipped.

## Learn More

To learn more about the AI SDK or Next.js by Vercel, take a look at the following resources:

- [AI SDK Documentation](https://sdk.vercel.ai/docs)
- [Next.js Documentation](https://nextjs.org/docs)
