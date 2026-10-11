import fs from 'node:fs';
import path from 'node:path';
import { POSTS_DIR } from '../site.config';
import { getAllPosts, postUrl, SHOW_DRAFT_PAGES } from './posts';

export type FileKind = 'markdown' | 'image' | 'video' | 'other';

export interface TreeNode {
  name: string;
  /** Путь относительно корня коллекции, через `/`. */
  path: string;
  type: 'dir' | 'file';
  kind?: FileKind;
  children: TreeNode[];
  /** Для папки поста и её index.md. */
  post?: { title: string; draft: boolean; href?: string };
}

const KINDS: Record<string, FileKind> = {
  '.md': 'markdown',
  '.png': 'image',
  '.jpg': 'image',
  '.jpeg': 'image',
  '.webp': 'image',
  '.avif': 'image',
  '.gif': 'image',
  '.mp4': 'video',
  '.webm': 'video',
};

/** Рекурсивно читает реальную структуру папок: сначала папки, потом файлы. */
function walk(abs: string, rel: string): TreeNode[] {
  return fs
    .readdirSync(abs, { withFileTypes: true })
    .filter((d) => !d.name.startsWith('.'))
    .sort((a, b) =>
      a.isDirectory() === b.isDirectory()
        ? a.name.localeCompare(b.name)
        : a.isDirectory() ? -1 : 1,
    )
    .map((d): TreeNode => {
      const p = rel ? `${rel}/${d.name}` : d.name;
      return d.isDirectory()
        ? { name: d.name, path: p, type: 'dir', children: walk(path.join(abs, d.name), p) }
        : {
            name: d.name,
            path: p,
            type: 'file',
            kind: KINDS[path.extname(d.name).toLowerCase()] ?? 'other',
            children: [],
          };
    });
}

/** Дерево папки коллекции, где папки постов размечены данными из коллекции. */
export async function getPostTree(): Promise<TreeNode[]> {
  const posts = new Map((await getAllPosts()).map((p) => [p.id, p]));

  const annotate = (nodes: TreeNode[]) => {
    for (const node of nodes) {
      const entry = posts.get(node.path);
      if (node.type === 'dir' && entry) {
        const post = {
          title: entry.data.title,
          draft: entry.data.draft,
          href: !entry.data.draft || SHOW_DRAFT_PAGES ? postUrl(entry.id) : undefined,
        };
        node.post = post;
        const index = node.children.find((c) => c.name === 'index.md');
        if (index) index.post = post;
      }
      annotate(node.children);
    }
  };

  const tree = walk(path.resolve(POSTS_DIR), '');
  annotate(tree);
  return tree;
}
