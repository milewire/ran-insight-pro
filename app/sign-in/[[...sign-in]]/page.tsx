import { SignIn } from '@clerk/nextjs'

export default function SignInPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-gray-50">
      <div className="w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-gray-900">RAN Insight Pro</h1>
          <p className="mt-2 text-gray-600">Sign in to your account</p>
        </div>
        <SignIn 
          appearance={{
            elements: {
              formButtonPrimary: 'bg-blue-600 hover:bg-blue-700 text-sm normal-case',
              card: 'shadow-lg',
            }
          }}
        />
      </div>
    </div>
  )
}
