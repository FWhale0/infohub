import type { Item } from '../../types/item'
import { FeedCard } from './FeedCard'

export function FeedList({ items }: { items: Item[] }) {
  return (
    <section id="items-list">
      {items.map((item) => (
        <FeedCard key={item.id} item={item} />
      ))}
    </section>
  )
}
