import { ExternalLink } from "lucide-react"

export function Footer() {
  return (
    <footer className="border-t border-border bg-card/30 backdrop-blur-sm mt-auto">
      <div className="container mx-auto px-4 py-6">
        <div className="flex items-center justify-between flex-wrap gap-4 text-sm text-muted-foreground">
          <div>
            <p>© 2025 Service de Mobilité </p>
            <p className="text-xs mt-1">Version 1.0.0</p>
          </div>
          <a
            href="/docs"
            className="flex items-center gap-2 hover:text-foreground transition-colors"
            target="_blank"
            rel="noopener noreferrer"
          >
            Documentation API
            <ExternalLink className="h-4 w-4" />
          </a>
        </div>
      </div>
    </footer>
  )
}
