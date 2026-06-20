import { Link } from 'react-router-dom'
import { Home } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { Card, CardContent } from '@/components/ui/card'

export default function NotFound() {
  return (
    <div className="flex items-center justify-center min-h-[60vh] p-8">
      <Card className="max-w-md w-full">
        <CardContent className="flex flex-col items-center text-center py-12">
          <p className="text-6xl font-bold text-muted-foreground/30 mb-4">404</p>
          <h1 className="text-xl font-semibold text-foreground mb-2">Page not found</h1>
          <p className="text-sm text-muted-foreground mb-6">
            The page you are looking for does not exist or has been moved.
          </p>
          <Button asChild>
            <Link to="/">
              <Home size={16} />
              Back to dashboard
            </Link>
          </Button>
        </CardContent>
      </Card>
    </div>
  )
}
