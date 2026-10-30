import { getCollection, type CollectionEntry } from 'astro:content';

export type Project = CollectionEntry<'projects'>;

/** Категории портфолио: папка в коллекции и подпись для человека. */
export const PROJECT_CATEGORIES = {
  'ai-automation': 'AI-автоматизация',
  'mobile-apps': 'Мобильные приложения',
} as const;

export type ProjectCategory = keyof typeof PROJECT_CATEGORIES;

export const projectUrl = (id: string) => `/проекты/${id}/`;

export const projectCategory = (id: string) => id.split('/')[0] as ProjectCategory;

/** Путь снимка лежит рядом с index.md, URL повторяет путь проекта. */
export const shotUrl = (id: string, file: string) => `${projectUrl(id)}${file}`;

const byOrder = (a: Project, b: Project) =>
  a.data.order - b.data.order || a.data.title.localeCompare(b.data.title);

export async function getAllProjects() {
  return (await getCollection('projects')).sort(byOrder);
}

/** Проекты, разложенные по категориям в объявленном порядке. */
export async function getProjectsByCategory() {
  const projects = await getAllProjects();
  return Object.keys(PROJECT_CATEGORIES)
    .map((category) => ({
      category: category as ProjectCategory,
      title: PROJECT_CATEGORIES[category as ProjectCategory],
      projects: projects.filter((p) => projectCategory(p.id) === category),
    }))
    .filter((group) => group.projects.length > 0);
}
