from scholarly import scholarly
from models import Session, Researcher, Publication
import time

def sync_researcher_pubs(researcher_id):
    session = Session()
    researcher = session.query(Researcher).get(researcher_id)
    
    if not researcher:
        session.close()
        raise Exception("Researcher not found")
    
    search_query = researcher.scholar_url if researcher.scholar_url else researcher.name
    print(f"Searching for: {search_query}")
    
    try:
        author = None
        if researcher.scholar_url and "user=" in researcher.scholar_url:
            # Extract user ID from URL
            user_id = researcher.scholar_url.split("user=")[1].split("&")[0]
            print(f"Fetching by Scholar ID: {user_id}")
            author = scholarly.search_author_id(user_id)
        else:
            # Try full name first
            print(f"Searching by name: {researcher.name}")
            search_results = scholarly.search_author(researcher.name)
            try:
                author = next(search_results)
            except StopIteration:
                # Fallback: Try just last name if name has multiple parts
                name_parts = researcher.name.split()
                if len(name_parts) > 1:
                    last_name = name_parts[-1]
                    print(f"No result for full name. Falling back to last name: {last_name}")
                    search_results = scholarly.search_author(last_name)
                    try:
                        author = next(search_results)
                    except StopIteration:
                        print("No author found in fallback.")
                else:
                    print("No author found.")
        
        if not author:
            session.close()
            return 0
        
        # Sort publications by citation count
        pubs = sorted(author['publications'], key=lambda x: x.get('num_citations', 0), reverse=True)[:10]
        
        # Clear existing publications for this researcher
        session.query(Publication).filter_by(researcher_id=researcher_id).delete()
        
        count = 0
        for p in pubs:
            # Fill individual publication details to get year/journal if possible
            # Note: fill(p) can be slow/trigger CAPTCHA, so we use summary data first
            title = p.get('bib', {}).get('title', 'Untitled')
            year = p.get('bib', {}).get('pub_year')
            journal = p.get('bib', {}).get('venue')
            citations = p.get('num_citations', 0)
            
            new_pub = Publication(
                researcher_id=researcher_id,
                title=title,
                year=int(year) if year else None,
                journal=journal,
                citation_count=citations,
                url=None # scholarly doesn't always provide a direct URL to the paper easily without more fills
            )
            session.add(new_pub)
            count += 1
            
        session.commit()
        return count
        
    except Exception as e:
        session.rollback()
        print(f"Error syncing {researcher.name}: {e}")
        raise e
    finally:
        session.close()

if __name__ == "__main__":
    # Test with a known ID if needed
    # sync_researcher_pubs('archangelsky_s')
    pass
