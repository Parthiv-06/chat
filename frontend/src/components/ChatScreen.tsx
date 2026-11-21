// One-to-one chat screen shown after login: you on the right, the other person on the left.
// History loads from /api/messages and new messages are polled every 2 s, deduplicated by id.
import * as React from "react"
import { ArrowUpIcon, LogOutIcon } from "lucide-react"
import { listMessages, sendMessage } from "@/api"
import {
  Chat,
  ChatInputArea,
  ChatInputField,
  ChatInputSubmit,
  ChatMessageAvatar,
  ChatMessageBubble,
  ChatMessageRow,
  ChatMessages,
  ChatMessageTime,
  ChatViewport,
  type ChatSubmitEvent,
} from "@/components/ui/chat"
import WindMap from "@/components/ui/wind-map"

type User = { id: number; username: string }

type ApiMessage = {
  id: number
  sender_id: number
  recipient_id: number
  body: string
  created_at: string
}

type Message = {
  id: number
  authorId: number
  content: string
  timestamp: Date
}

const POLL_MS = 2000

// Module-level so WindMap's effect sees a stable array and doesn't restart on each render.
const WIND_COLORS: [string, string, string, string] = ["#070a10", "#2b3d5c", "#7d9cc8", "#f0d9b5"]

const fromApi = (m: ApiMessage): Message => ({
  id: m.id,
  authorId: m.sender_id,
  content: m.body,
  timestamp: new Date(m.created_at),
})

// Adds incoming messages that aren't shown yet; a sent message can also arrive via polling.
function merge(prev: Message[], incoming: ApiMessage[]): Message[] {
  const seen = new Set(prev.map((m) => m.id))
  const fresh = incoming.filter((m) => !seen.has(m.id)).map(fromApi)
  return fresh.length ? [...prev, ...fresh].sort((a, b) => a.id - b.id) : prev
}

type ChatScreenProps = {
  me: User
  peer: User | null
  onLogout: () => void
}

const initial = (name: string) => name.trim().charAt(0).toUpperCase() || "?"

// Served by the backend only to logged-in users; the initial shows if it's missing or loading.
const avatarUrl = (userId: number) => `/api/avatars/${userId}`

export default function ChatScreen({ me, peer, onLogout }: ChatScreenProps) {
  const [messages, setMessages] = React.useState<Message[]>([])
  const [input, setInput] = React.useState("")
  const [error, setError] = React.useState("")
  // Advanced only by polls: a sent message's id can be newer than one the poll hasn't fetched yet.
  const lastPolledId = React.useRef<number | undefined>(undefined)
  const peerName = peer?.username ?? "them"

  React.useEffect(() => {
    let cancelled = false
    let timer: ReturnType<typeof setTimeout>
    const tick = async () => {
      try {
        const incoming: ApiMessage[] = await listMessages(lastPolledId.current)
        if (cancelled) return
        if (incoming.length) lastPolledId.current = incoming[incoming.length - 1].id
        setMessages((prev) => merge(prev, incoming))
      } catch {
        // Offline or server restarting: keep what's on screen and try again next tick.
      }
      if (!cancelled) timer = setTimeout(tick, POLL_MS)
    }
    tick()
    return () => {
      cancelled = true
      clearTimeout(timer)
    }
  }, [])

  const handleSubmit = async (e: ChatSubmitEvent) => {
    const text = e.message
    setInput("")
    setError("")
    try {
      const saved: ApiMessage = await sendMessage(text)
      setMessages((prev) => merge(prev, [saved]))
    } catch (err) {
      setInput(text)
      setError(err instanceof Error ? err.message : "Message not sent")
    }
  }

  return (
    <WindMap colors={WIND_COLORS} className="dark text-foreground h-dvh w-full">
      <Chat onSubmit={handleSubmit}>
        <div className="mx-auto flex h-full min-h-0 w-full max-w-2xl flex-col gap-3 px-3 pt-3 pb-[max(0.75rem,env(safe-area-inset-bottom))] sm:gap-4 sm:px-4 sm:py-6">
          <header className="flex items-center gap-3 px-1">
            <ChatMessageAvatar
              className="size-9 self-center"
              src={peer ? avatarUrl(peer.id) : undefined}
              fallback={initial(peerName)}
              alt={peerName}
            />
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-semibold">{peerName}</p>
              <p className="text-muted-foreground text-xs">you are {me.username}</p>
            </div>
            <button
              type="button"
              onClick={onLogout}
              className="text-muted-foreground hover:text-foreground -mr-2 flex items-center gap-1.5 rounded-md px-2 py-2 text-xs transition-colors"
            >
              <LogOutIcon className="size-3.5" />
              Log out
            </button>
          </header>

          <ChatViewport className="bg-card/55 min-h-0 flex-1 px-3 backdrop-blur-[2px] sm:px-4">
            <ChatMessages className="w-full py-3">
              <div className="text-muted-foreground my-6 text-center text-xs">
                {peer ? `Chat started with ${peerName}` : "The other person hasn't been set up yet"}
              </div>
              {messages.map((m) => {
                const mine = m.authorId === me.id
                const name = mine ? me.username : peerName
                return (
                  <ChatMessageRow key={m.id} variant={mine ? "self" : "peer"}>
                    <ChatMessageAvatar src={avatarUrl(m.authorId)} fallback={initial(name)} alt={name} />
                    <ChatMessageBubble className="max-w-[calc(100vw-7.5rem)] sm:max-w-96">
                      {m.content}
                    </ChatMessageBubble>
                    <ChatMessageTime dateTime={m.timestamp} />
                  </ChatMessageRow>
                )
              })}
            </ChatMessages>
          </ChatViewport>

          {error && <p className="text-destructive px-1 text-xs" role="alert">{error}</p>}
          <ChatInputArea className="bg-background/70 backdrop-blur-sm">
            <ChatInputField
              multiline
              placeholder={`Message ${peerName}`}
              value={input}
              onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setInput(e.target.value)}
            />
            <ChatInputSubmit disabled={!input.trim()}>
              <ArrowUpIcon className="size-[1.2em]" />
              <span className="sr-only">Send</span>
            </ChatInputSubmit>
          </ChatInputArea>
        </div>
      </Chat>
    </WindMap>
  )
}
