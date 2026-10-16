"""Generate Vercel build and routing configuration from the site's URL table."""
import re

def configuration(pages, migrations):
    routes = []
    for migration in migrations:
        status = migration['status']
        if status == 200:
            continue
        for path in sorted({migration['old_path'], migration['old_path'].rstrip('/') + '/'}):
            if path == migration['destination']:
                continue
            route = {'src': '^' + re.escape(path) + '$', 'status': status}
            if status == 301:
                route['headers'] = {'Location': migration['destination']}
            else:
                route['dest'] = '/410.html'
            routes.append(route)
    for path in pages:
        destination = '/index.html' if path == '/' else path.rstrip('/') + '/index.html'
        source = '^/$' if path == '/' else '^' + re.escape(path.rstrip('/')) + '/?$'
        routes.append({'src': source, 'dest': destination})
    routes.extend([{'handle': 'filesystem'}, {'src': '/(.*)', 'dest': '/404.html', 'status': 404}])
    return {
        '$schema': 'https://openapi.vercel.sh/vercel.json',
        'framework': None,
        'installCommand': '',
        'buildCommand': 'python3 tools/build.py',
        'outputDirectory': 'dist',
        'routes': routes,
    }
