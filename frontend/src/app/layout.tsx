import { Providers } from './providers'

export const metadata = {
  title: 'Evolve Agent',
  description: 'Generate n8n workflows using natural language',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>
        <Providers>{children}</Providers>
      </body>
    </html>
  )
}
